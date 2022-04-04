import discord
from discord.ext import commands

import json
from os import environ

class kimoshine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MAIMAIID = int(environ["MAIMAIID"])
        self.ADMIN = int(environ["ADMINID"])
  
    @commands.command()
    async def edit(self, ctx, mode, word):
        """きもしね対象語句のリストを編集します"""      
        if ctx.author.id not in [self.ADMIN,self.MAIMAIID]:
            return
        with open("data/kimoshine.json", "r") as f:
            d = json.load(f)
        if mode == "add":
            if word in d["badword"]:
                await ctx.channel.send("既に追加されています")
                return
            d["badword"].append(word)
            with open("data/kimoshine.json", "w") as f:
                json.dump(d, f)
        elif mode == "remove":
            if word not in d["badword"]:
                await ctx.channel.send("存在しない言葉です")
                return
            d["badword"].remove(word)
            with open("data/kimoshine.json", "w") as f:
                json.dump(d, f)
        else:
            await ctx.channel.send("コマンドが間違っています")
        await ctx.channel.send("処理を反映しました")

    @commands.command()
    async def kimoshinelist(self, ctx):
        """きもしね対象リストを表示します"""
        with open("data/kimoshine.json", "r") as f:
            d = json.load(f)
        msg = ",".join(d["badword"])
        embed = discord.Embed(title="きもしねリスト", description=msg)
        await ctx.channel.send(embed=embed)


def setup(bot):
    return bot.add_cog(kimoshine(bot))
