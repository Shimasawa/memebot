import discord
from discord.ext import commands

import aiosqlite

from time import time
import datetime

class Huu(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    async def huu(self,ctx):
        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                raw = await cursor.execute(
                    "select * from ふぅ計測 where ユーザーid = ?",
                    [ctx.author.id]
                )
                raw = await raw.fetchone()
                
                #開始する場合
                #データ新規作成の場合
                if raw == None:
                    await cursor.execute(
                        "insert into ふぅ計測(ユーザーid,開始) values(?,?)",
                        [ctx.author.id,time()]
                    )
                    raw = [ctx.author.id,0]
                    await db.commit()
                    await ctx.channel.send("データベースに新規登録しました")
                #新たに開始
                if raw[1] == 0:
                    await cursor.execute(
                        "update ふぅ計測 set 開始 = ? where ユーザーid = ?",
                        [time(),ctx.author.id]
                    )
                    await db.commit()
                    await ctx.channel.send("開始しました")
                    return

                #終了する場合
                if raw[1] != 0:
                    result = time()-raw[1]
                    if raw[2] == None or result < raw[2]:
                        await cursor.execute(
                            "update ふぅ計測 set 最速 = ? where ユーザーid = ?",
                            [result,ctx.author.id]
                        )
                        await ctx.channel.send("最速記録更新！")
                    if raw[3] == None or result > raw[3]:
                        await cursor.execute(
                            "update ふぅ計測 set 最長 = ? where ユーザーid = ?",
                            [result,ctx.author.id]
                        )
                        await ctx.channel.send("最長記録更新！")
                    await cursor.execute(
                        "update ふぅ計測 set 開始 = 0 where ユーザーid = ?",
                        [ctx.author.id]
                    )
                    await db.commit()
                    td = datetime.timedelta(seconds=result)
                    m,s = divmod(td.seconds,60)
                    await ctx.channel.send(f"{m}分{s}秒")

def setup(bot):
    return bot.add_cog(Huu(bot))