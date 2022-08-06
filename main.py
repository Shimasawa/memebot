import discord
from discord.ext import commands
import jishaku

from os import listdir, environ

from dotenv import load_dotenv

intents = discord.Intents.default()

load_dotenv()
TOKEN = environ['TOKEN_KUROKAGE']
PREFIX = environ["PREFIX"]

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
cogs = [cog[:-3] for cog in listdir("cog") if cog.endswith(".py")]

bot.load_extension("jishaku")

for cog in cogs:
    bot.load_extension(f"cog.{cog}")

bot.run(TOKEN)