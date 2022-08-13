import discord
from discord.ext import commands

import aiosqlite

import json
from os import environ
from time import time
from asyncio import sleep

from module import decorater

class Pin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.ADMINID = int(environ["ADMINID"])
    

    @commands.command()
    @commands.check(decorater.is_admin)
    async def pin(self,ctx,desc=None):
        db = await aiosqlite.connect("data/main.db")
        cursor = await db.cursor()
        if desc == None:
            await cursor.execute("delete from 強制ピン止め where チャンネルid = ?",[ctx.channel.id])
        else:
            await cursor.execute("select count(*) from 強制ピン止め where チャンネルid = ?",[ctx.channel.id])
            count = await cursor.fetchone()
            if count[0] == 0:
                await cursor.execute("insert into 強制ピン止め values(?,?,?,?)",[ctx.channel.id,time(),desc,None])
            else:
                await cursor.execute("update 強制ピン止め set 前回実行 = ?,内容 = ?,前回メッセージ where チャンネルid = ?",[time(),desc,ctx.channel.id,None])
        await db.commit()
        await cursor.close()
        await db.close()
        await ctx.channel.send("変更が完了しました")
    
    @commands.Cog.listener()
    async def on_message(self,ctx):
        if ctx.author.bot:
            return
        db = await aiosqlite.connect("data/main.db")
        cursor = await db.cursor()
        raw = await cursor.execute("select 前回実行,内容,前回メッセージ from 強制ピン止め where チャンネルid = ?",[ctx.channel.id])
        raw = await raw.fetchone()
        if raw == None:
            return
        if (time()-raw[0]) > 10:
            if raw[2] != None:
                try:
                    past_msg = await ctx.channel.fetch_message(raw[2])
                    await past_msg.delete()
                except:
                    pass
            msg = await ctx.channel.send(raw[1])
            await cursor.execute("update 強制ピン止め set 前回実行 = ?,前回メッセージ = ? where チャンネルid = ?",[time(),msg.id,ctx.channel.id])
            await db.commit()
        await cursor.close()
        await db.close()
            

def setup(bot):
  return bot.add_cog(Pin(bot))