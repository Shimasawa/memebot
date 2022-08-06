import discord
from discord.ext import commands

import json
import jaconv

from os import environ

class Message(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
    self.PENID = int(environ["PENID"])
    self.ADMIN = int(environ["ADMINID"])
    self.CHLIST = [int(environ["MOEECHID"]),
                   int(environ["NSFWID"]),
                   int(environ["ONEESANID"])]

  @commands.Cog.listener("on_message")
  async def onmessage(self,ctx):
    
    #無視する処理
    if ctx.author.bot:
      return
    if ctx.content.startswith("k!"):
      return

    #ペンさんであった場合の処理
    if ctx.author.id == self.PENID and ctx.content != "ふぅ":
      with open("data/huu.json") as f:
        d = json.load(f)
      if d["recent"] != 0:
        d["recent"] = 0
        with open("data/huu.json","w") as f:
          json.dump(d,f,indent=4)
      
    if ctx.author.id == self.PENID and ctx.content == "ふぅ":
      with open("data/huu.json") as f:
        d = json.load(f)
      d["total"] += 1
      d["recent"] += 1
      if (d["recent"]%3) == 0:
        await ctx.reply(f"{d['recent']}コンボ!")
        await ctx.author.edit(nick="おじさんのファン")
      with open("data/huu.json","w") as f:
        json.dump(d,f,indent=4)
      
    if ctx.author.id == self.PENID and ctx.channel.id not in self.CHLIST:
      with open("data/pen.json","r",encoding="utf-8") as f:
        d = json.load(f)
      for i in d.keys():
        if i in jaconv.h2z(ctx.content):
          d[i]["count"] += 1
          with open("data/pen.json","w") as f:
            json.dump(d,f,indent=4)
          await ctx.reply("数値を追加しました")
          await ctx.author.edit(nick="おじさんのファン")
          break

    #共通の処理
    with open("data/kimoshine.json","r") as f:
      d = json.load(f)
    flag = False
    for i in d["badword"]:
      if i in ctx.content:
        flag = True
        break
    if flag:        
      await ctx.reply("きもしね")
      if ctx.author.id == self.PENID:
        await ctx.author.edit(nick="おじさんのファン")

def setup(bot):
  return bot.add_cog(Message(bot))