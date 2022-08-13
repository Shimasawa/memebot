from os import environ
from discord.ext import commands

ADMINID = int(environ["ADMINID"])
PENID = int(environ["PENID"])

def is_admin(ctx: commands.Context):
    return ctx.author.id == ADMINID