import discord
from discord.ext import commands

import aiosqlite

from os import environ
from time import time

from module import confirm

class Pin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.PREFIX = environ["PREFIX"]
        self.COOLDOWN = 10

    @commands.command()
    @commands.check(confirm.is_admin)
    async def pin(self,ctx,desc=None):
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
                        "select count(*) from 強制ピン止め where チャンネルid = ?",
                        [ctx.channel.id]
                        )
                    count = await cursor.fetchone()
                    #ピンが無かった場合
                    if count[0] == 0:
                        await cursor.execute(
                            "insert into 強制ピン止め values(?,?,?,?)",
                            [ctx.channel.id,time(),desc,None]
                            )
                    #ピンが既にあった場合
                    else:
                        await cursor.execute(
                            "update 強制ピン止め set 前回実行 = ?,内容 = ?,前回メッセージ = ? where チャンネルid = ?",
                            [time(),desc,None,ctx.channel.id]
                            )
                await db.commit()
                await ctx.channel.send("変更が完了しました")
    
    
    @commands.Cog.listener()
    async def on_message(self,ctx):
        if ctx.author.bot or ctx.content.startswith(self.PREFIX):
            return
        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                raw = await cursor.execute(
                    "select 前回実行,内容,前回メッセージ from 強制ピン止め where チャンネルid = ?",
                    [ctx.channel.id]
                    )
                raw = await raw.fetchone()
                #ピンが無かった場合
                if raw == None:
                    return
                #前回のピンを送信してから十秒経過していた場合
                if (time()-raw[0]) > self.COOLDOWN:
                    if raw[2] != None:
                        #前回のメッセージを取得できた場合、できなかった場合
                        try:
                            past_msg = await ctx.channel.fetch_message(raw[2])
                            await past_msg.delete()
                        except:
                            pass
                    msg = await ctx.channel.send(raw[1])
                    await cursor.execute(
                        "update 強制ピン止め set 前回実行 = ?,前回メッセージ = ? where チャンネルid = ?",
                        [time(),msg.id,ctx.channel.id]
                        )
                    await db.commit()
            

def setup(bot):
  return bot.add_cog(Pin(bot))