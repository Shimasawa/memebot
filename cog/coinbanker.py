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
    async def sumcoin(self,ctx,triger_message: discord.Message):
        await ctx.channel.send("読み込み中")
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

            coin = re.search(r"[0-9]+",msg.content)
            if coin is None:
                continue
            
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
    async def set_num(self,ctx,user_id,num):
        if int(ctx.author.id) != self.ADMIN:
            await ctx.channel.send("管理者以外の実行")
            return

        with open("data/coin.json","r") as f:
            d = json.load(f)
        d[str(user_id)]["num"] = int(num)
        with open("data/coin.json","w") as f:
            json.dump(d,f,indent=2)
        await ctx.channel.send("設定しました")
    
    @commands.command()
    async def look_num(self,ctx,user_id=None):
        if int(ctx.author.id) != self.ADMIN:
            await ctx.channel.send("管理者以外の実行")
            return
        with open("data/coin.json","r") as f:
            d = json.load(f)
        
        if user_id == None:
            await ctx.channel.send("```json\n{}```".format(str(d)))
        else:
            await ctx.channel.send(str(d[str(user_id)]["num"]))
    
    @commands.command()
    async def name_list(self,ctx):
        if int(ctx.author.id) != self.ADMIN:
            await ctx.channel.send("管理者以外の実行")
            return
        await ctx.channel.send("読み込み中")
        with open("data/coin.json","r") as f:
            d = json.load(f)
        d = dict(sorted(d.items(),key=lambda x:x[1]["num"],reverse=True))
        l = []
        l2 = []
        l3 = []
        for i in d.keys():
            l2.append(d[i]["num"])
            l3.append(d[i]["count"])
            l.append(i)
        await ctx.channel.send(embed=discord.Embed(
          title="寄付ランキング",
          description="\n".join(["<@{}>\n寄付額:{}, 記録回数:{}".format(uid,num,count) for uid,num,count in zip(l,l2,l3)])
        ))

def setup(bot):
    return bot.add_cog(CoinBanker(bot))