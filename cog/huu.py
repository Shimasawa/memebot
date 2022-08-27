import discord
from discord.ext import commands

import aiosqlite

from time import time

class Huu(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    def to_ms(self,seconds: float) -> tuple:
        m,s = divmod(seconds,60)
        return int(m),int(s)
    
    @commands.command()
    async def huu(self,ctx,mode=None):
        #選択肢以外の場合
        if mode not in [None,"log","del"]:
            await ctx.channel.send(embed=discord.Embed(
                title="存在しない引数",
                description="`huu`->計測の開始&終了\n`huu log`->記録の表示\n`huu del`->記録の削除"
            ))
            return

            
        async with aiosqlite.connect("data/main.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute("select * from ふぅ計測 where ユーザーid = ?",[ctx.author.id])
                raw = await cursor.fetchone()
                if mode in ["log","del"] and raw == None:
                    await ctx.channel.send("データが存在しません")
                    return

                
                #計測mode(引数=None),開始=0は開始していない状態
                if mode == None:
                    #開始する場合
                    #データ新規作成の場合
                    if raw == None:
                        raw = [ctx.author.id,0]
                        await cursor.execute("insert into ふぅ計測(ユーザーid,開始) values(?,?)",raw)
                        await db.commit()
                        await ctx.channel.send("データベースに新規登録しました")
                    #新たに開始
                    if raw[1] == 0:
                        await cursor.execute(
                            "update ふぅ計測 set 開始 = ? where ユーザーid = ?",
                            [time(),ctx.author.id]
                        )
                        await db.commit()
                        await ctx.channel.send("開始しました")
                        return

                    #終了する場合
                    if raw[1] != 0:
                        result = time()-raw[1]
                        if raw[2] == None or result < raw[2]:
                            await cursor.execute(
                                "update ふぅ計測 set 最速 = ? where ユーザーid = ?",
                                [result,ctx.author.id]
                            )
                            await ctx.channel.send("最速記録更新！")
                        if raw[3] == None or result > raw[3]:
                            await cursor.execute(
                                "update ふぅ計測 set 最長 = ? where ユーザーid = ?",
                                [result,ctx.author.id]
                            )
                            await ctx.channel.send("最長記録更新！")
                        await cursor.execute("update ふぅ計測 set 開始 = 0 where ユーザーid = ?",[ctx.author.id])
                        await db.commit()
                        m,s = divmod(int(result),60)
                        await ctx.channel.send(embed=discord.Embed(
                            title=f"{ctx.author.display_name}の今回の記録",
                            description=f"{m}分{s}秒"
                        ))

                
                #最長・最短記録閲覧mode(引数=log)
                elif mode == "log":
                    #raw[2]とraw[3]が無い=初回計測中なので記録は出さない
                    if raw[2] == None or raw[3] == None:
                        await ctx.channel.send("記録が存在しません")
                        return
                    fastest = self.to_ms(raw[2])
                    latest = self.to_ms(raw[3])
                    await ctx.channel.send(embed=discord.Embed(
                        title=f"{ctx.author.display_name}のふぅ記録",
                        description=f"最速 : {fastest[0]}分{fastest[1]}秒\n最長 : {latest[0]}分{latest[1]}秒",
                    ))


                #データ削除mode(引数=del)
                elif mode == "del":            
                    await cursor.execute("delete from ふぅ計測 where ユーザーid = ?",[ctx.author.id])
                    await db.commit()
                    await ctx.channel.send("データを削除しました")

def setup(bot):
    return bot.add_cog(Huu(bot))