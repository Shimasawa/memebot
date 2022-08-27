import discord
from discord.ext import commands

import aiosqlite

import re
import json
from os import environ

from module import confirm

class CoinBanker(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ADMIN = int(environ["ADMINID"])
        self.PREFIX = environ["PREFIX"]
    
    @commands.command()
    @commands.check(confirm.is_admin)
    @commands.check(confirm.is_coin_log_ch)
    async def sumcoin(self,ctx,triger_message: discord.Message):
        await ctx.channel.send("読み込み中")
        #メッセージ取得
        try:
            message_list = [message async for message in ctx.channel.history(limit=None,after=triger_message)]
        except:
            await ctx.channel.send("メッセージの取得に失敗しました")
            return
        
        await ctx.channel.send(f"{len(message_list)}件のメッセージを取得しました。\n記録を開始します")
        
        for msg in message_list:
            
            msg: discord.Message

            if msg.content.startswith(self.PREFIX) or msg.author.bot:
                continue

            #数字探索
            coin = re.search(r"[0-9]+",msg.content)
            if coin is None:
                continue
            #追加
            coin = int(coin.group())
            async with aiosqlite.connect("data/main.db") as db:
                async with db.cursor() as cursor:
                    await cursor.execute("select * from クラコ集計 where ユーザーid = ?",[msg.author.id])
                    raw = await cursor.fetchone()
                    if raw is None:
                        raw = [msg.author.id,0,0]
                        await cursor.execute("insert into クラコ集計 values(?,?,?)",raw)
                        await db.commit()
                    await cursor.execute(
                        "update クラコ集計 set 総額 = ?,記録回数 = ? where ユーザーid = ?",
                        [raw[1]+coin,raw[2]+1,msg.author.id]
                    )
                    await db.commit()
        await ctx.channel.send("記録を終了しました")
    
    @commands.command()
    async def users_coin(self,ctx,target: discord.User):
        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("select 総額,記録回数 from クラコ集計 where ユーザーid = ?",[target.id])
                raw = await cursor.fetchone()
                if raw is None:
                    await ctx.channel.send("データが存在しません")
                    return
                else:
                    await ctx.channel.send(embed=discord.Embed(
                        title=f"{target.display_name}の記録",
                        description=f"総額 : {raw[0]}\n記録回数 : {raw[1]}"
                    ))
    
    @commands.command()
    async def coinrank(self,ctx):
        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("select * from クラコ集計 order by 総額 desc")
                str_raw = []
                count = 1
                async for data in cursor:
                    try:
                        user = await self.bot.fetch_user(data[0])
                        str_raw.append(f"{count}位.{user.display_name}\n総額: {data[1]}, 記録回数: {data[2]}")
                        count += 1
                    except:
                        pass
                await ctx.channel.send(embed=discord.Embed(
                    title="クランコイン寄付ランキング",
                    description="\n".join(str_raw)
                ))

def setup(bot):
    return bot.add_cog(CoinBanker(bot))