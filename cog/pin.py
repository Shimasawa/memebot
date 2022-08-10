import discord
from discord.ext import commands

import json
from os import environ

class Pin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ADMINID = int(environ["ADMINID"])
    
    @commands.command()
    async def pin(self,ctx,desc=None):
        """管理者専用"""
        if ctx.author.id != self.ADMINID:
            await ctx.reply("あなたにはこのコマンドを実行する権限がありません")
            return
        with open("data/pin.json","r") as f:
            d = json.load(f)
        if desc == None:
            if d.get(str(ctx.channel.id)) != None:
                del d[str(ctx.channel.id)]
            else:
                await ctx.channel.send("このチャンネルにはピンが設定されていません")
                return
        else:
            d[str(ctx.channel.id)] = {
                "desc":desc,
                "past":0
            }
        with open("data/pin.json","w") as f:
            json.dump(d,f,indent=4)
        await ctx.reply("変更を確定しました")
    
    @commands.Cog.listener()
    async def on_message(self,ctx):
        if ctx.author.bot:
            return
        with open("data/pin.json","r") as f:
            d = json.load(f)
        ch_pin = d.get(str(ctx.channel.id))
        if ch_pin == None:
            return
        if d[str(ctx.channel.id)]["past"] != 0:
            try:
                past_msg = await ctx.channel.fetch_message(d[str(ctx.channel.id)]["past"])
                await past_msg.delete()
            except:
                pass
        msg = await ctx.channel.send(d[str(ctx.channel.id)]["desc"])
        d[str(ctx.channel.id)]["past"] = msg.id
        with open("data/pin.json","w") as f:
            json.dump(d,f,indent=4)

def setup(bot):
  return bot.add_cog(Pin(bot))