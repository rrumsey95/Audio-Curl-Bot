import discord
import yt_dlp
import asyncio
import random
import os
from discord import app_commands
from .core import bot, tree
from .queue import Song, queues, ensure_queue

COOKIES_FILE = os.getenv("YTDLP_COOKIES", "cookies.txt")  # You can set this in your .env

@tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    try:
        await interaction.response.defer(ephemeral=True)  # Acknowledge the interaction early
        if queue["vc"] and queue["vc"].is_connected():
            await interaction.followup.send("I'm already connected to a voice channel.", ephemeral=True)
            return
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            vc = await channel.connect()
            queues[interaction.guild.id]["vc"] = vc
            await interaction.followup.send("🎤 Joined your voice channel!")
        else:
            await interaction.followup.send("You need to join a voice channel first.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to join voice channel: {e}", ephemeral=True)

@tree.command(name="play_playlist", description="Play a YouTube playlist")
@app_commands.describe(url="YouTube playlist URL")
async def play_playlist(interaction: discord.Interaction, url: str):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    vc = queue["vc"]
    if not vc or not vc.is_connected():
        await interaction.response.send_message("Bot must be in a voice channel. Use `/join` first.", ephemeral=True)
        return

    await interaction.response.send_message("⏳ Fetching playlist...")
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'force_generic_extractor': True,
        'cookiesfromfile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info.get('entries', [])
        if not entries:
            await interaction.followup.send("❌ No videos found.")
            return

    for entry in entries:
        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
        queue["songs"].append(Song(entry["title"], video_url, video_url, interaction.user))

    await interaction.followup.send(f"✅ Added `{len(entries)}` songs to the queue.")
    if not queue["playing"]:
        await play_next(interaction.guild.id)

@tree.command(name="play", description="Play a single YouTube video")
@app_commands.describe(url="YouTube video URL")
async def play(interaction: discord.Interaction, url: str):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    vc = queue["vc"]
    if not vc or not vc.is_connected():
        await interaction.response.send_message("Bot must be in a voice channel. Use `/join` first.", ephemeral=True)
        return

    await interaction.response.send_message("⏳ Fetching video...")
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'cookiesfromfile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info:
            await interaction.followup.send("❌ No video found.")
            return

    queue["songs"].append(Song(info["title"], url, info.get("webpage_url", url), interaction.user))
    await interaction.followup.send(f"✅ Added `{info['title']}` to the queue.")
    if not queue["playing"]:
        await play_next(interaction.guild.id)

async def play_next(guild_id):
    await ensure_queue(guild_id)
    queue = queues[guild_id]
    if not queue["songs"]:
        queue["playing"] = False
        return

    song = queue["songs"].pop(0)
    vc = queue["vc"]
    queue["playing"] = True

    stream_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'noplaylist': True,
        'cookiesfromfile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
    }

    with yt_dlp.YoutubeDL(stream_opts) as ydl:
        info = ydl.extract_info(song.url, download=False)
        audio_url = info['url']

    source = discord.FFmpegPCMAudio(audio_url)
    vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(guild_id), bot.loop))
    text_channel = discord.utils.get(vc.guild.text_channels, name="general") or vc.guild.system_channel
    if text_channel:
        await text_channel.send(embed=song.embed())

@tree.command(name="skip", description="Skip the current song")
async def skip(interaction: discord.Interaction):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    if queue["vc"] and queue["vc"].is_playing():
        queue["vc"].stop()
        await interaction.response.send_message("⏭ Skipping...")
    else:
        await interaction.response.send_message("Nothing is playing.", ephemeral=True)

@tree.command(name="pause", description="Pause playback")
async def pause(interaction: discord.Interaction):
    queue = queues.get(interaction.guild.id, {})
    if queue.get("vc") and queue["vc"].is_playing():
        queue["vc"].pause()
        await interaction.response.send_message("⏸ Paused.")
    else:
        await interaction.response.send_message("Nothing is playing.", ephemeral=True)

@tree.command(name="resume", description="Resume playback")
async def resume(interaction: discord.Interaction):
    queue = queues.get(interaction.guild.id, {})
    if queue.get("vc") and queue["vc"].is_paused():
        queue["vc"].resume()
        await interaction.response.send_message("▶️ Resumed.")
    else:
        await interaction.response.send_message("Nothing to resume.", ephemeral=True)

@tree.command(name="queue", description="View the upcoming songs")
async def view_queue(interaction: discord.Interaction):
    queue = queues.get(interaction.guild.id, {})
    songs = queue.get("songs", [])
    if not songs:
        await interaction.response.send_message("Queue is empty.")
        return

    embed = discord.Embed(title="🎶 Song Queue", color=discord.Color.blurple())
    for i, song in enumerate(songs[:10], 1):
        embed.add_field(name=f"{i}. {song.title}", value=f"[Link]({song.webpage_url}) — Requested by {song.requested_by.display_name}", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="leave", description="Disconnect the bot")
async def leave(interaction: discord.Interaction):
    queue = queues.get(interaction.guild.id)
    try:
        if queue and queue.get("vc") and queue["vc"].is_connected():
            await queue["vc"].disconnect()
            queue["vc"] = None
            queue["songs"].clear()
            queue["playing"] = False
            await interaction.response.send_message("👋 Left the voice channel and cleared the queue.")
        else:
            await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to leave voice channel: {e}", ephemeral=True)

@tree.command(name="shuffle", description="Shuffle the current song queue")
async def shuffle(interaction: discord.Interaction):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    songs = queue.get("songs", [])
    if len(songs) < 2:
        await interaction.response.send_message("Need at least two songs in the queue to shuffle.", ephemeral=True)
        return
    random.shuffle(songs)
    await interaction.response.send_message("🔀 The queue has been shuffled!")

@tree.command(name="clear_queue", description="Clear all songs from the queue")
async def clear_queue(interaction: discord.Interaction):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    if not queue["songs"]:
        await interaction.response.send_message("The queue is already empty.", ephemeral=True)
        return
    queue["songs"].clear()
    await interaction.response.send_message("🗑️ The song queue has been cleared.", ephemeral=True)

@tree.command(name="remove", description="Remove a song from the queue by its position")
@app_commands.describe(position="Position in the queue (starts at 1)")
async def remove(interaction: discord.Interaction, position: int):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    songs = queue.get("songs", [])
    if position < 1 or position > len(songs):
        await interaction.response.send_message("Invalid position.", ephemeral=True)
        return
    removed = songs.pop(position - 1)
    await interaction.response.send_message(f"🗑️ Removed `{removed.title}` from the queue.")

@tree.command(name="nowplaying", description="Show the currently playing song")
async def nowplaying(interaction: discord.Interaction):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    vc = queue.get("vc")
    if not vc or not vc.is_playing():
        await interaction.response.send_message("Nothing is currently playing.", ephemeral=True)
        return
    # The currently playing song is not stored directly, so you may want to keep track of it.
    # For now, let's assume you store it as queue["current_song"]
    current_song = getattr(queue, "current_song", None)
    if not current_song:
        await interaction.response.send_message("No song info available.", ephemeral=True)
        return
    await interaction.response.send_message(embed=current_song.embed())

@tree.command(name="volume", description="Set the playback volume (0-100)")
@app_commands.describe(level="Volume level (0-100)")
async def volume(interaction: discord.Interaction, level: int):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    vc = queue.get("vc")
    if not vc or not (vc.is_playing() or vc.is_paused()):
        await interaction.response.send_message("Nothing is playing.", ephemeral=True)
        return
    if not (0 <= level <= 100):
        await interaction.response.send_message("Volume must be between 0 and 100.", ephemeral=True)
        return
    # discord.py does not support volume control directly on FFmpegPCMAudio after creation.
    # You'd need to recreate the source with a new volume filter.
    await interaction.response.send_message("Volume adjustment is not currently supported.", ephemeral=True)

@tree.command(name="help", description="Show available commands and their descriptions")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Audio-Curl-Bot Commands",
        description="Here are the available commands:",
        color=discord.Color.green()
    )
    embed.add_field(name="/join", value="Join your voice channel.", inline=False)
    embed.add_field(name="/play_playlist", value="Play an entire YouTube playlist. Usage: `/play_playlist <playlist_url>`", inline=False)
    embed.add_field(name="/play", value="Play a single YouTube video. Usage: `/play <video_url>`", inline=False)
    embed.add_field(name="/queue", value="View the upcoming songs.", inline=False)
    embed.add_field(name="/skip", value="Skip the current song.", inline=False)
    embed.add_field(name="/pause", value="Pause playback.", inline=False)
    embed.add_field(name="/resume", value="Resume playback.", inline=False)
    embed.add_field(name="/shuffle", value="Shuffle the current song queue.", inline=False)
    embed.add_field(name="/clear_queue", value="Clear all songs from the queue.", inline=False)
    embed.add_field(name="/remove", value="Remove a song from the queue by its position. Usage: `/remove <position>`", inline=False)
    embed.add_field(name="/nowplaying", value="Show the currently playing song.", inline=False)
    embed.add_field(name="/volume", value="Set the playback volume (not currently supported). Usage: `/volume <0-100>`", inline=False)
    embed.add_field(name="/leave", value="Disconnect the bot and clear the queue.", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

