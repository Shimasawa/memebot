import discord
from discord.ext import commands

import re
import json
from os import environ

class Sumcoin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ADMIN = int(environ["ADMINID"])
    
    @commands.command()
    async def cal_ch_num(self,ctx,message_id,limit_num):
        
        if int(ctx.author.id) != self.ADMIN:
            await ctx.channel.send("管理者以外の実行")
            return

        await ctx.channel.send("読み込み中")
        
        l = []
        
        async for message in ctx.channel.history(limit=int(limit_num)+2):

            l.append(message)
            
            if message.id == int(message_id):
                break
        
        if len(l) == int(limit_num):
            await ctx.channel.send("メッセージを取得できませんでした。\n__取得したメッセージのリスト__")
            await ctx.channel.send("\n".join([m.content for m in l]))
            return

        await ctx.channel.send(f"{len(l)}件のメッセージを取得しました")

        with open("data/coin.json","r") as f:
            d = json.load(f)
        
        for i in l:
                        
            if "k!" in i.content or i.author.bot:
                continue
            num = re.search(r"[0-9]+",i.content)
            if num == None:
                continue

            if str(i.author.id) not in d.keys():
                d[str(i.author.id)] = {
                    "num":0,
                    "count":0
                }
            d[str(i.author.id)]["num"] += int(num.group())
            d[str(i.author.id)]["count"] += 1
        with open("data/coin.json","w") as f:
            json.dump(d,f,indent=2)
        await ctx.channel.send("処理を終了しました")
        try:
            await ctx.channel.send("__取得したメッセージリスト__\n```{}```".format("\n".join([m.content for m in l])))
        except:
            await ctx.channel.send("取得した中で最も古いメッセージ\n{}".format(l[-1].content))
    
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
    return bot.add_cog(Sumcoin(bot))