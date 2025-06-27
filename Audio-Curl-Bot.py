import discord
from discord.ext import commands, tasks
from discord import app_commands
import yt_dlp
import asyncio
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for bot token, etc.)
load_dotenv()

# Set up Discord bot intents (controls what events the bot can see)
intents = discord.Intents.default()
intents.message_content = True  # Needed for message content access

# Create the bot instance with a command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # For slash commands

# Dictionary to store song queues and voice connections per guild (server)
queues = {}

# Song class to represent each song in the queue
class Song:
    def __init__(self, title, url, webpage_url, requested_by):
        self.title = title
        self.url = url
        self.webpage_url = webpage_url
        self.requested_by = requested_by

    # Create a Discord embed for the "Now Playing" message
    def embed(self):
        return discord.Embed(
            title=f"🎶 Now Playing: {self.title}",
            url=self.webpage_url,
            description=f"Requested by {self.requested_by.mention}",
            color=discord.Color.purple()
        )

# Ensure a queue exists for the given guild (server)
async def ensure_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = {
            "songs": [],
            "playing": False,
            "vc": None
        }

# Event: Called when the bot is ready and connected to Discord
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await tree.sync()  # Sync slash commands with Discord
    print("Slash commands synced.")

# Slash command: Join the user's voice channel
@tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    try:
        # Only connect if not already connected
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

# Slash command: Play all songs from a YouTube playlist
@tree.command(name="play_playlist", description="Play a YouTube playlist")
@app_commands.describe(url="YouTube playlist URL")
async def play_playlist(interaction: discord.Interaction, url: str):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    vc = queue["vc"]
    # Must be in a voice channel to play music
    if not vc or not vc.is_connected():
        await interaction.response.send_message("Bot must be in a voice channel. Use `/join` first.", ephemeral=True)
        return

    await interaction.response.send_message("⏳ Fetching playlist...")
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'force_generic_extractor': True,
    }

    # Use yt-dlp to extract playlist info
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info.get('entries', [])
        if not entries:
            await interaction.followup.send("❌ No videos found.")
            return

    # Add each song in the playlist to the queue
    for entry in entries:
        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
        queue["songs"].append(Song(entry["title"], video_url, video_url, interaction.user))

    await interaction.followup.send(f"✅ Added `{len(entries)}` songs to the queue.")
    # Start playback if not already playing
    if not queue["playing"]:
        await play_next(interaction.guild.id)

# Play the next song in the queue for a guild
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

    # Use yt-dlp to get the audio stream URL
    with yt_dlp.YoutubeDL(stream_opts) as ydl:
        info = ydl.extract_info(song.url, download=False)
        audio_url = info['url']

    # Play the audio in the voice channel
    source = discord.FFmpegPCMAudio(audio_url)
    vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(guild_id), bot.loop))
    # Send "Now Playing" message to the general or system channel
    text_channel = discord.utils.get(vc.guild.text_channels, name="general") or vc.guild.system_channel
    if text_channel:
        await text_channel.send(embed=song.embed())

# Slash command: Skip the current song
@tree.command(name="skip", description="Skip the current song")
async def skip(interaction: discord.Interaction):
    await ensure_queue(interaction.guild.id)
    queue = queues[interaction.guild.id]
    if queue["vc"] and queue["vc"].is_playing():
        queue["vc"].stop()
        await interaction.response.send_message("⏭ Skipping...")
    else:
        await interaction.response.send_message("Nothing is playing.", ephemeral=True)

# Slash command: Pause playback
@tree.command(name="pause", description="Pause playback")
async def pause(interaction: discord.Interaction):
    queue = queues.get(interaction.guild.id, {})
    if queue.get("vc") and queue["vc"].is_playing():
        queue["vc"].pause()
        await interaction.response.send_message("⏸ Paused.")
    else:
        await interaction.response.send_message("Nothing is playing.", ephemeral=True)

# Slash command: Resume playback
@tree.command(name="resume", description="Resume playback")
async def resume(interaction: discord.Interaction):
    queue = queues.get(interaction.guild.id, {})
    if queue.get("vc") and queue["vc"].is_paused():
        queue["vc"].resume()
        await interaction.response.send_message("▶️ Resumed.")
    else:
        await interaction.response.send_message("Nothing to resume.", ephemeral=True)

# Slash command: Show the current song queue
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

# Slash command: Disconnect the bot and clear the queue
@tree.command(name="leave", description="Disconnect the bot")
async def leave(interaction: discord.Interaction):
    queue = queues.get(interaction.guild.id)
    try:
        # Only disconnect if connected
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

# Start the bot using the token from the .env
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
