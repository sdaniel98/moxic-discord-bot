import os
from dotenv import load_dotenv
from discord.ext import commands




if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv("MOXIC_DISCORD_TOKEN")

    bot = commands.Bot(command_prefix="#")

    @bot.event
    async def on_ready():
        print(f"Successfully attached to {bot.user}")

    bot.run(TOKEN)

