from bot.core import bot
import bot.commands  # Registers all commands
import bot.core  

import os
# bot.run(os.getenv("DISCORD_BOT_TOKEN"))
if __name__ == "__main__":
    # Run the bot
    bot.core.run()