import discord
from discord.ext import commands

import aiosqlite

from os import environ
import asyncio

from module import confirm

class Pin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.PREFIX: str = environ["PREFIX"]
        self.COOLDOWN = 5
        self.cd = commands.CooldownMapping.from_cooldown(1,self.COOLDOWN,commands.BucketType.channel)
    
    def ratelimit(self,msg: discord.Message):
        bucket = self.cd.get_bucket(msg)
        return bucket.update_rate_limit()

    @commands.command()
    @commands.check(confirm.is_admin)
    async def pin(self,ctx,desc: str=None):
        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                #ピンを削除する場合
                if desc == None:
                    await cursor.execute(
                        "delete from 強制ピン止め where チャンネルid = ?",
                        [ctx.channel.id]
                        )
                #ピンを追加する場合
                else:
                    await cursor.execute(
                        "select * from 強制ピン止め where チャンネルid = ?",
                        [ctx.channel.id]
                        )
                    #ピンが無かった場合
                    if await cursor.fetchone() is None:
                        await cursor.execute(
                            "insert into 強制ピン止め values(?,?,?)",
                            [ctx.channel.id,desc,None]
                            )
                    #ピンが既にあった場合
                    else:
                        await cursor.execute(
                            "update 強制ピン止め set 内容 = ?,前回メッセージ = ? where チャンネルid = ?",
                            [desc,None,ctx.channel.id]
                            )
                await db.commit()
                await ctx.channel.send("変更が完了しました")
    
    
    @commands.Cog.listener()
    async def on_message(self,ctx):
        if ctx.author.bot or ctx.content.startswith(self.PREFIX) or self.ratelimit(ctx) is not None:
            return
        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                raw = await cursor.execute(
                    "select 内容,前回メッセージ from 強制ピン止め where チャンネルid = ?",
                    [ctx.channel.id]
                    )
                raw = await raw.fetchone()
                #ピンが無かった場合
                if raw is None:
                    return
                #前回のピンを送信してから十秒経過していた場合
                await asyncio.sleep(self.COOLDOWN)
                if raw[1] != None:
                    #前回のメッセージを取得できた場合、できなかった場合
                    try:
                        past_msg: discord.Message = await ctx.channel.fetch_message(raw[1])
                        await past_msg.delete()
                    except:
                        pass
                msg: discord.Message = await ctx.channel.send(raw[0])
                await cursor.execute(
                    "update 強制ピン止め set 前回メッセージ = ? where チャンネルid = ?",
                    [msg.id,ctx.channel.id]
                    )
                await db.commit()
            

def setup(bot):
  return bot.add_cog(Pin(bot))