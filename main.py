import discord
from discord.ext import commands
import jishaku

from server import keep_alive

from os import listdir, environ
import traceback

intents = discord.Intents.default()

token = environ['TOKEN']

bot = commands.Bot(command_prefix="k!", intents=intents)

cogs = [cog[:-3] for cog in listdir("cog") if cog.endswith(".py")]

bot.load_extension("jishaku")

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(
        traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


for cog in cogs:
    bot.load_extension(f"cog.{cog}")

keep_alive()
bot.run(token)
