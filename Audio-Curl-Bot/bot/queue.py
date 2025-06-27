import discord

class Song:
    def __init__(self, title, url, webpage_url, requested_by):
        self.title = title
        self.url = url
        self.webpage_url = webpage_url
        self.requested_by = requested_by

    def embed(self):
        return discord.Embed(
            title=f"🎶 Now Playing: {self.title}",
            url=self.webpage_url,
            description=f"Requested by {self.requested_by.mention}",
            color=discord.Color.purple()
        )

queues = {}

async def ensure_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = {
            "songs": [],
            "playing": False,
            "vc": None
        }