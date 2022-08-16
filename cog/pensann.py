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
    async def old_huu(self,ctx,mode):
        """ふぅTA(start,end)"""
        if ctx.author.id not in [self.ADMIN,self.PENID]:
            return
        if ctx.channel.id != int(environ["NSFWID"]):
            return
        with open("data/time.json","r") as f:
            d = json.load(f)
        if mode == "start":
            if d["is_start"]:
                await ctx.send("既に計測中です")
                return
            else:
                d["time"] = time()
                d["is_start"] = True
                with open("data/time.json","w") as f:
                    json.dump(d,f,indent=4)
                await ctx.send("スタートしました")
        elif mode == "end":
            if d["is_start"]:
                t = time()-d["time"]
                await ctx.send(f"タイム : {t}秒")
                d["is_start"] = False
                with open("data/time.json","w") as f:
                    json.dump(d,f,indent=4)
            else:
                await ctx.send("開始していません")
                return
        else:
            await ctx.send("引数はstart,endです")
            return
    
    @commands.command()
    async def saranuki(self,ctx):
        with open("data/huu.json") as f:
            d = json.load(f)
        await ctx.send(f"現在{d['recent']}コンボ中！合計{d['total']}回")

    @commands.command()
    async def penword(self,ctx,mode,ward,fine_type,amount):
        """ポイントを追加する文字列リストを編集します"""
        if ctx.author.id != self.ADMIN:
            return
        if mode == "add":
            with open("data/pen.json","r") as f:
                d = json.load(f)
            d[ward] = {
                "count":0,
                "type":fine_type,
                "amount":int(amount)
            }
            with open("data/pen.json","w") as f:
                json.dump(d,f,indent=4)
            await ctx.channel.send("追加しました")
        elif mode == "remove":
            with open("data/pen.json","r") as f:
                d = json.load(f)
            del d[ward]
            with open("data/pen.json","w") as f:
                json.dump(d,f,indent=4)
            await ctx.channel.send("削除しました")
            

    @commands.command()
    async def pencount(self,ctx,ward,count):
        """カウント対象の文字に対して指定した数字を設定します"""
        if ctx.author.id != self.ADMIN:
            return
        with open("data/pen.json","r") as f:
            d = json.load(f)
        d[ward]["count"] = int(count)
        with open("data/pen.json","w") as f:
            json.dump(d,f,indent=4)
        await ctx.channel.send("変更を確定しました")
      
    @commands.command()
    async def pennow(self,ctx):
      """今のキル数などを表示します"""
      with open("data/pen.json","r") as f:
        d = json.load(f)
      kill = 0
      damage = 0
      for i in d.keys():
        if d[i]["type"] == "kill":
          kill += d[i]["amount"]*d[i]["count"]
        elif d[i]["type"] == "damage":
          damage += d[i]["amount"]*d[i]["count"]
      embed = discord.Embed(title="キル数カウンター",description="キル数とダメージは別カウント")
      embed.add_field(name="キル数",value=f"{kill}キル")
      embed.add_field(name="ダメージ数",value=f"{damage}ダメージ")
      await ctx.channel.send(embed=embed)

    @commands.command()
    async def show_list(self,ctx):
        with open("data/pen.json","r") as f:
            d = json.load(f)
        msg = "\n".join([i for i in d.keys()])
        embed = discord.Embed(title="カウントワード一覧",description=msg)
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def pen_send_data(self,ctx):
        """pen.jsonの辞書データを送信します"""
        if ctx.author.id != self.ADMIN:
            return
        with open("data/pen.json","r") as f:
            d = json.load(f)
        await ctx.channel.send(str(d))

    @commands.command()
    async def penpoint(self,ctx,mode,fine_type,count):
        """ポイントを追加・減少させます"""
        if ctx.author.id != self.ADMIN:
            return
        with open("data/pen.json","r") as f:
            d = json.load(f)
        if mode == "remove":
            if fine_type == "damage":
                d["へへへ"]["count"] -= int(count)
            elif fine_type == "kill":
                d["お姉さん"]["count"] -= int(count)
        elif mode == "add":
            if fine_type == "damage":
                d["へへへ"]["count"] += int(count)
            elif fine_type == "kill":
                d["お姉さん"]["count"] += int(count)
        with open("data/pen.json","w") as f:
            json.dump(d,f,indent=4)
        await ctx.channel.send("ポイントに反映しました")
        
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