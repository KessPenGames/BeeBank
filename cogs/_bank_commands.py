import disnake
from disnake.ext import commands

from bank import bank_user, user_card, cards_logs
from configs import config
from exceptions.bank_exception import CardNotFound, NotEnoughMoney
from generators.card_image.card import generate
from logs import discord_logs
from messages.history_embed import CardHistoryEmbed
from models.models import User, Card
from utils.mine_converters import usernameToUuid, uuidToUsername
from views import buttons
from utils import check as mainbool


class CommandsCog(commands.Cog):
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
            await ctx.send(f"Была создана карта **{name}** под номером **{card.id}** для **{card.user}**")
            await discord_logs.sendLog(
                ctx.guild, 4,
                ctx.author.name, str(card.user), str(card.id)
            )

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def add(self, ctx: commands.Context, card_id: int, amount: int):
        sender = await user_card.addMoney(config.getAttr("bank-card-id"), amount)
        receiver = await user_card.addMoney(card_id, amount)
        await ctx.send(f"На карту **{receiver.name}** было начислено **{amount}АР**")
        banker = await bank_user.getUser(ctx.author.id)

        await cards_logs.addLog(1, card_id, config.getAttr("bank-card-id"), f'{str(amount)}|Банкир {str(banker)}')
        await cards_logs.addLog(1, config.getAttr("bank-card-id"), card_id, f'{str(amount)}|Банкир {str(banker)}')

        await discord_logs.sendLog(
            ctx.guild, 1,
            uuidToUsername(receiver.user.mc_uuid),
            uuidToUsername(sender.user.mc_uuid),
            f'{str(amount)}|Банкир {str(banker)}'
        )
        await discord_logs.sendLog(
            ctx.guild, 2,
            uuidToUsername(sender.user.mc_uuid),
            uuidToUsername(receiver.user.mc_uuid),
            f'{str(amount)}|Банкир {str(banker)}'
        )

        await discord_logs.sendNotification(
            ctx.guild.get_member(receiver.user.discord_id), 1,
            uuidToUsername(sender.user.mc_uuid),
            f'{str(amount)}|Банкир {str(banker)}'
        )

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def take(self, ctx: commands.Context, card_id: int, amount: int):
        sender = await user_card.removeMoney(config.getAttr("bank-card-id"), amount)
        receiver = await user_card.removeMoney(card_id, amount)
        await ctx.send(f"С карты **{receiver.name}** было списано **{amount}АР**")
        banker = await bank_user.getUser(ctx.author.id)

        await cards_logs.addLog(2, card_id, config.getAttr("bank-card-id"), f'{str(amount)}|Банкир {str(banker)}')
        await cards_logs.addLog(2, config.getAttr("bank-card-id"), card_id, f'{str(amount)}|Банкир {str(banker)}')

        await discord_logs.sendLog(
            ctx.guild, 2,
            uuidToUsername(receiver.user.mc_uuid),
            uuidToUsername(sender.user.mc_uuid),
            f'{str(amount)}|Банкир {str(banker)}'
        )
        await discord_logs.sendLog(
            ctx.guild, 1,
            uuidToUsername(sender.user.mc_uuid),
            uuidToUsername(receiver.user.mc_uuid),
            f'{str(amount)}|Банкир {str(banker)}'
        )

        await discord_logs.sendNotification(
            ctx.guild.get_member(receiver.user.discord_id), 2,
            receiver.name, str(amount)
        )

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
    async def update_id(self, ctx: commands.Context, old_id: int, new_id: int):
        if mainbool.isAuthor(ctx):
            await user_card.updateCardId(old_id, new_id)
            await ctx.send(f"ID карты {old_id} было сменено на {new_id}")

    @commands.command()
    async def getAllCards(self, ctx: commands.Context):
        if mainbool.isAuthor(ctx):
            cards = await user_card.getAllCards()
            for card in cards:
                await ctx.send(f'{str(card.id)}: {str(card.balance)}')

    @commands.command()
    async def updateNick(self, ctx: commands.Context, user_id: int, nickname: str):
        if mainbool.isAuthor(ctx):
            await bank_user.updateMCUuid(user_id, usernameToUuid(nickname))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CardNotFound):
            await ctx.send("Карта не найдена.")
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("Введён неправильный аргумент.")
        if isinstance(error, NotEnoughMoney):
            await ctx.send("Не хватает средств.")
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.send("Комманда не найдена")


def setup(bot=commands.Bot):
    bot.add_cog(CommandsCog(bot))
    print(f"Cog {__name__} is loading!")