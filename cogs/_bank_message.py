from disnake.ext import commands, tasks

from views import buttons
from utils import check as mainbool
from generators.random_day_image import day_image
from configs import config


class MessageCog(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.send_task.start()

    @commands.command()
    async def send(self, ctx: commands.Context):
        if mainbool.isAuthor(ctx):
            await self.send_bank_message(ctx.channel)

    @tasks.loop(hours=24)
    async def send_task(self):
        await self.send_bank_message(
            self.bot.get_guild(config.getAttr("guild-id")).get_channel(config.getAttr("send-channel-id"))
        )

    async def send_bank_message(self, channel):
        await channel.purge(limit=10)
        await channel.send(embed=await day_image.random_img(channel.guild.get_member(config.getAttr("bot-id")).avatar.url))
        await channel.send(
            "Приветствуем вас в меню управлением **BeeBank**, здесь представлены основные,"
            " доступные вам функции.", view=buttons.BankButtons()
        )


def setup(bot=commands.Bot):
    bot.add_cog(MessageCog(bot))
    print(f"Cog {__name__} is loading!")