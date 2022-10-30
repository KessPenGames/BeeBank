from disnake.ext import commands

from bank import bank_user, user_card, cards_logs
from utils.mine_converters import usernameToUuid
from utils import check as mainbool


class UpdateCommandsCog(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command()
    async def update_id(self, ctx: commands.Context, old_id: int, new_id: int):
        if mainbool.isAuthor(ctx):
            await user_card.updateCardId(old_id, new_id)
            await cards_logs.updateOneCard(old_id, new_id)
            await cards_logs.updateTwoCard(old_id, new_id)
            await ctx.send(f"ID карты {old_id} было сменено на {new_id}")

    @commands.command()
    async def updateNick(self, ctx: commands.Context, user_id: int, nickname: str):
        if mainbool.isAuthor(ctx):
            await bank_user.updateMCUuid(user_id, usernameToUuid(nickname))


def setup(bot=commands.Bot):
    bot.add_cog(UpdateCommandsCog(bot))
    print(f"Cog {__name__} is loading!")