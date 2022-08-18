import discord
from discord.ext import commands

import json
import random

import aiosqlite

from os import environ
from time import time

class Pensan(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.PENID = int(environ["PENID"])
        self.ADMIN = int(environ["ADMINID"])
        self.CHLIST = [int(environ["MOEECHID"]),
                       int(environ["NSFWID"]),
                       int(environ["ONEESANID"])]
    
    @commands.command()
    async def saranuki(self,ctx):
        with open("data/huu.json") as f:
            d = json.load(f)
        await ctx.send(f"現在{d['recent']}コンボ中！合計{d['total']}回")
        
    @commands.command(name="du-yo-one-san?")
    async def test(self,ctx):
        """該当チャンネルのログ300件から画像を抽選・送信します"""
        if ctx.author.id != self.PENID:
            return
        if ctx.channel.id not in self.CHLIST:
            return
        await ctx.channel.send("画像を取得中...")
        attachment = []
        try:
            async for row in ctx.channel.history(limit=(300)):
                try:
                    if row.attachments[0].filename.endswith((".png",".jpg",".HEIC",".jpeg",".JPEG")):
                        attachment.append(row.attachments[0])
                except:
                    pass
            f = random.choice(attachment)
            f = await f.to_file()
            await ctx.channel.send(f"{len(attachment)}件の画像を取得しました",file=f)
        except:
            await ctx.channel.send("画像が見つかりませんでした")
def setup(bot):
  return bot.add_cog(Pensan(bot))