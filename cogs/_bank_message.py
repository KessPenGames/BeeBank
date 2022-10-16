from disnake.ext import commands

from views import buttons
from utils import check as mainbool


class MessageCog(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command()
    async def send(self, ctx):
        if mainbool.isAuthor(ctx):
            await ctx.send(
                "Приветствую вас в меню управлением **BeeBank**, здесь представлены основные,"
                " доступные вам функции.", view=buttons.BankButtons()
            )


def setup(bot=commands.Bot):
    bot.add_cog(MessageCog(bot))
    print(f"Cog {__name__} is loading!")
