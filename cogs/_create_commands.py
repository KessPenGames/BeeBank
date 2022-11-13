from disnake.ext import commands

from bank import bank_user, user_card, cards_logs
from configs import config
from logs_handlers import discord_logs
from utils.mine_converters import usernameToUuid


class CreateCommandsCog(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def create_user(self, ctx: commands.Context, user_id: int, nickname: str):
        uuid = usernameToUuid(nickname)
        if uuid:
            await bank_user.add_user(user_id, usernameToUuid(nickname))
            await ctx.send(f"Был создан новый пользователь в банке **{nickname}**")
            await discord_logs.sendLog(
                ctx.guild, 3,
                ctx.author.name, nickname, ""
            )

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def create_card(self, ctx: commands.Context, user_id: int, *name: str):
        name = " ".join(name[:])
        name = "Стандартный счёт" if name != " " and "" else name
        if await bank_user.getUser(user_id):
            card = await user_card.addCard(user_id, name)
            await user_card.addMoney(config.getAttr("grant-card-id"), 5)
            await cards_logs.addLog(1, config.getAttr("grant-card-id"), card.id,
                                    f'5|Банкир {ctx.author.name}, создание карты.')
            await ctx.send(f"Была создана карта **{name}** под номером **{card.id}** для **{card.user}**")
            await discord_logs.sendLog(
                ctx.guild, 4,
                ctx.author.name, str(card.user), str(card.id)
            )


def setup(bot=commands.Bot):
    bot.add_cog(CreateCommandsCog(bot))
    print(f"Cog {__name__} is loading!")