from bot.core import bot
import bot.commands  # Registers all commands

import os
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
