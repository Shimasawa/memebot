import discord
from discord.ext import commands

import aiosqlite

from module.confirm import is_admin,is_ignore_ch,is_pen

class PenWord(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    @commands.check(is_admin)
    async def penword(self,ctx,mode=None,word=None):
        if mode not in [None,"add","del"]:
            await ctx.channel.send(embed=discord.Embed(
                title="間違った引数",
                description="`penword`->登録言語一覧表示\n`penword add <word>`->記録の表示\n`penword del <word>`->記録の削除"
            ))
            return
        elif mode in ["add","del"] and word == None:
            await ctx.channel.send("追加&削除する言語を指定してください")
            return

        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                #登録言語一覧を表示(mode=None)
                if mode == None:
                    await cursor.execute("select * from ペン言語")
                    result = "\n".join(["{},{}".format(w,c) for w,c in await cursor.fetchall() if w != None or c != None])
                    await ctx.channel.send(embed=discord.Embed(
                        title="登録言語一覧",
                        description="<単語>,<カウント>\n"+result
                    ))


                #言語追加    
                elif mode == "add":
                    await cursor.execute("select * from ペン言語 where 単語 = ?",[word])
                    if await cursor.fetchone() != None:
                        await ctx.channel.send("既に登録されています")
                    else:
                        await cursor.execute("insert into ペン言語 values(?,0)",[word])
                        await db.commit()
                        await ctx.channel.send("新規登録しました")
                

                elif mode == "del":
                    await cursor.execute("select * from ペン言語 where 単語 = ?",[word])
                    if await cursor.fetchone() == None:
                        await ctx.channel.send("存在しない値です")
                    else:
                        await cursor.execute("delete from ペン言語 where 単語 = ?",[word])
                        await db.commit()
                        await ctx.channel.send("削除しました")
                    
                return

    @commands.Cog.listener()
    async def on_message(self,ctx: discord.Message):
        if is_ignore_ch(ctx.channel.id) or ctx.author.bot or not is_pen(ctx):
            return
        
        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("select * from ペン言語")
                async for word in cursor:
                    if word[0] in ctx.content:
                        if ((word[1]+1)%10) == 0:
                            await ctx.author.edit(nick="おじさんのファン")
                        await cursor.execute(
                            "update ペン言語 set カウント = ? where 単語 = ?",
                            [word[1]+1,word[0]]
                        )
                        await db.commit()


def setup(bot):
    return bot.add_cog(PenWord(bot))