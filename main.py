import os
from dotenv import load_dotenv
from discord.ext import commands

extensions = ["cogs.Developer",
              "cogs.LogShamer",
              "cogs.Miscellaneous"]

if __name__ == '__main__':
    load_dotenv("./Authentication Files/.env")
    TOKEN = os.getenv("MOXIC_DISCORD_TOKEN")

    bot = commands.Bot(command_prefix="#")

    for ext in extensions:
        try:
            bot.load_extension(ext)
            print(f"Successfully loaded: {ext}")
        except Exception as e:
            print(f"Failed to load: {ext}")
            print(e)

    @bot.event
    async def on_ready():
        print(f"Successfully connected to {bot.user}")

    bot.run(TOKEN)

