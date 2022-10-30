import disnake
from disnake.ext import commands

from bank import bank_user, user_card
from configs import config
from generators.card_image.card import generate
from messages.history_embed import CardHistoryEmbed
from models.models import User, Card
from views import buttons
from utils import check as mainbool


class GetCommandsCog(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def getId(self, ctx: commands.Context, tag: str):
        try:
            name, tag = tag.split('#')
            user = disnake.utils.get(ctx.guild.members, name=name, discriminator=tag)
            if user:
                await ctx.send(str(user.id))
        except ValueError:
            pass

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def getUser(self, ctx: commands.Context, nickname: str):
        user: User = await bank_user.getUserByNickname(nickname)
        if user:
            await ctx.send(str(user.discord_id))

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def getCards(self, ctx: commands.Context, user_id: int):
        cards = await user_card.getCardsByUserId(user_id)
        for card in cards:
            await ctx.send(f'{str(card.id)}: {card.name}')

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def history(self, ctx: commands.Context, card_id: int):
        che = CardHistoryEmbed(card_id)
        embed = che.getPage()
        if embed:
            await ctx.send(embed=embed, view=buttons.HistoryButtons(
                che.isNext(), che.isPrevious(), 1, card_id
            ))

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def card(self, ctx: commands.Context, card_id: int):
        card: Card = await user_card.getCard(card_id)
        color = tuple(int(card.text_color[i:i + 2], 16) for i in (0, 2, 4))
        await ctx.send(file=generate(card.background, str(card.balance), card.name, card.id, color))

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def check(self, ctx: commands.Context):
        balance = 0
        cards = await user_card.getAllCards()
        for card in cards:
            balance = balance + card.balance
        await ctx.send(f"В казне должно быть {balance}")

    @commands.command()
    async def getAllCards(self, ctx: commands.Context):
        if mainbool.isAuthor(ctx):
            cards = await user_card.getAllCards()
            for card in cards:
                await ctx.send(f'{str(card.id)}: {str(card.balance)}')


def setup(bot=commands.Bot):
    bot.add_cog(GetCommandsCog(bot))
    print(f"Cog {__name__} is loading!")