import discord
from discord.ext import commands

import aiosqlite

from os import environ
from random import choice

class Pensan(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.PENID = int(environ["PENID"])
        self.CH = int(environ["ONEESANID"])
        
    @commands.command()
    async def onesan(self,ctx):
        if ctx.channel.id != self.CH:
            await ctx.channel.send("お姉さんチャンネルでのみ有効")
            return
        
        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("select * from おねえさん画像集")
                msg_id = choice([i async for i in cursor])[0]
                print(msg_id)
                try:
                    msg: discord.Message = await ctx.channel.fetch_message(msg_id)
                    img = choice(msg.attachments)
                    img = await img.to_file()
                    await ctx.channel.send(file=img)
                except:
                    await ctx.channel.send("抽選された画像を取得できませんでした")
                return
    
    @commands.Cog.listener()
    async def on_message(self,ctx: discord.Message):
        if ctx.author.id != self.PENID or len(ctx.attachments) == 0:
            return
        
        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("insert into おねえさん画像集 values(?)",[ctx.id])
                await db.commit()
                


def setup(bot):
  return bot.add_cog(Pensan(bot))