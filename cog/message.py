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
    if ctx.author.id == self.PENID and ctx.channel.id not in self.CHLIST:
      with open("data/pen.json","r",encoding="utf-8") as f:
        d = json.load(f)
      for i in d.keys():
        if i in jaconv.h2z(ctx.content):
          d[i]["count"] += 1
          with open("data/pen.json","w") as f:
            json.dump(d,f,indent=4)
          await ctx.reply("数値を追加しました")
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
        await ctx.send("https://cdn.discordapp.com/attachments/891488747638624326/966316611357265971/IMG_2671.jpg")

def setup(bot):
  return bot.add_cog(Message(bot))