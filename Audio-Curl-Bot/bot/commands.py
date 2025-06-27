import discord
import yt_dlp
import asyncio
from discord import app_commands
from .core import bot, tree
from .queue import Song, queues, ensure_queue

@tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    try:
        if queue["vc"] and queue["vc"].is_connected():
            await interaction.response.send_message("I'm already connected to a voice channel.", ephemeral=True)
            return
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            vc = await channel.connect()
            queues[interaction.guild.id]["vc"] = vc
            await interaction.response.send_message("🎤 Joined your voice channel!")
        else:
            await interaction.response.send_message("You need to join a voice channel first.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to join voice channel: {e}", ephemeral=True)

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
        'noplaylist': True
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