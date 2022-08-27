from os import environ
from discord.ext import commands

ADMINID = int(environ["ADMINID"])
PENID = int(environ["PENID"])
IGNORE_CHANNE_ID = [
    int(environ["MOEECHID"]),
    int(environ["NSFWID"]),
    int(environ["ONEESANID"])
]
COIN_LOG_CH_ID = int(environ["COIN_LOG_CH_ID"])
PREFIX = environ["PREFIX"]

def is_admin(ctx: commands.Context):
    return ctx.author.id == ADMINID

def is_not_mycommand(ctx: commands.Context):
    return not ctx.message.content.startswith(PREFIX)

def is_ignore_ch(channel_id: int):
    return channel_id in IGNORE_CHANNE_ID

def is_pen(ctx: commands.Context):
    return ctx.author.id == PENID

def is_coin_log_ch(ctx: commands.Context):
    return ctx.channel.id == COIN_LOG_CH_ID