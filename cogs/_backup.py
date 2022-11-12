from disnake.ext import commands, tasks

from utils import check as mainbool
from backup import backuping


class BackupCog(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot
        self.backup_task.start()

    def cog_unload(self):
        self.backup_task.cancel()

    @commands.command()
    async def backup(self, ctx):
        if mainbool.isAuthor(ctx):
            await backuping()
            await ctx.send("БД была бэкапнута!")

    @tasks.loop(hours=1)
    async def backup_task(self):
        print("DB Backup started...")
        await backuping()
        print("Backup over!")


def setup(bot=commands.Bot):
    bot.add_cog(BackupCog(bot))
    print(f"Cog {__name__} is loading!")