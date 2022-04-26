import discord
from discord.ext import commands
import jishaku

from server import keep_alive

from os import listdir, environ

intents = discord.Intents.default()

token = environ['TOKEN']

bot = commands.Bot(command_prefix="k!", intents=intents)

cogs = [cog[:-3] for cog in listdir("cog") if cog.endswith(".py")]

bot.load_extension("jishaku")

for cog in cogs:
    bot.load_extension(f"cog.{cog}")

keep_alive()
bot.run(token)
