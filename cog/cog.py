import datetime
import os

from discord.ext import commands, tasks  # Bot Commands Frameworkのインポート

from cog.util.DbModule import DbModule as db


class Sleep(commands.Cog):

   def __init__(self, bot) -> None:
      self.bot = bot
      self.printer.start()
      self.db = db()

   @commands.slash_command(name="おやすみタイム")
   async def sleeps(self, ctx, start: str, end: str):
      user = self.db.select(f"select *from sleeptime where id={ctx.author.id}")
      if user == []:
         self.db.allinsert("sleeptime", [ctx.author.id, start, end, 0])

      await ctx.respond(f"おやすみタイムを設定しました。解除するまで{start}から{end}まではボイスチャットに入れません")
      start = start.replace(":", "/")
      end = end.replace(":", "/")
      self.db.update("sleeptime", {"start": start, "end": end, "status": 1}, {"id": ctx.author.id})

   @commands.slash_command(name="おやすみタイム解除")
   async def sleeps_delete(self, ctx):
      self.db.update("sleeptime", {"start": "0", "end": "0", "status": 0}, {"id": ctx.author.id})
      await ctx.ctx.respond("おやすみタイムを解除しました")

   async def sleep_time_process(self, nowtime):
      users = self.db.select("select *from sleeptime where start!='0'")
      for user in users:
         channel = self.bot.get_channel(os.getenv("SEND_CHANNEL"))
         starttime: str = user["start"]
         starthour = int(starttime.split("/")[0])
         startminute = int(starttime.split("/")[1])
         endtime: str = user["end"]
         endhour = int(endtime.split("/")[0])
         endminute = int(endtime.split("/")[1])
         if nowtime.hour == starthour and nowtime.minute == startminute:
            member = self.bot.get_user(user['id'])
            self.db.update("sleeptime", {"status": 1}, {"id": user["id"]})
            await channel.send(f"{member.mention}おやすみタイムに突入しました")
            vcchannel = self.bot.get_channel(os.getenv("SEND_CHANNEL"))
            for member in vcchannel.members:
               if member.id == user["id"]:
                  await member.move_to(None)

         elif nowtime.hour == endhour and nowtime.minute == endminute:
            self.db.update("sleeptime", {"status": 0}, {"id": user["id"]})
            member = self.bot.get_user(user['id'])
            await channel.send(f"{member.mention}おやすみタイムが終わりました")

   @tasks.loop(seconds=60.0)
   async def printer(self):
      nowtime = datetime.datetime.now()
      await self.sleep_time_process(nowtime)


def setup(bot):
   bot.add_cog(Sleep(bot))
