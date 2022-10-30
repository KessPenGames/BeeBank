import base64

from disnake.ext import commands

from bank import bank_user, user_card, cards_logs
from configs import config
from exceptions.bank_exception import CardNotFound, NotEnoughMoney
from generators.card_image.card import generate, random_img
from logs_handlers import discord_logs
from utils.mine_converters import uuidToUsername
from views import buttons
from utils import check as mainbool


class CommandsCog(commands.Cog):
    def __init__(self, bot=commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def add(self, ctx: commands.Context, card_id: int, amount: int):
        receiver = await user_card.addMoney(card_id, amount)
        await ctx.send(f"На карту **{receiver.name}** было начислено **{amount}АР**")
        banker = await bank_user.getUser(ctx.author.id)

        await cards_logs.addLog(1, card_id, config.getAttr("bank-card-id"), f'{str(amount)}|Банкир {str(banker)}')

        await discord_logs.sendLog(
            ctx.guild, 1,
            uuidToUsername(receiver.user.mc_uuid),
            "BBank",
            f'{str(amount)}|Банкир {str(banker)}'
        )
        await discord_logs.sendLog(
            ctx.guild, 2,
            "BBank",
            uuidToUsername(receiver.user.mc_uuid),
            f'{str(amount)}|Банкир {str(banker)}'
        )

        await discord_logs.sendNotification(
            ctx.guild.get_member(receiver.user.discord_id), 1,
            "BBank",
            f'{str(amount)}|Банкир {str(banker)}'
        )

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def take(self, ctx: commands.Context, card_id: int, amount: int):
        receiver = await user_card.removeMoney(card_id, amount)
        await ctx.send(f"С карты **{receiver.name}** было списано **{amount}АР**")
        banker = await bank_user.getUser(ctx.author.id)

        await cards_logs.addLog(2, card_id, config.getAttr("bank-card-id"), f'{str(amount)}|Банкир {str(banker)}')

        await discord_logs.sendLog(
            ctx.guild, 2,
            uuidToUsername(receiver.user.mc_uuid),
            "BBank",
            f'{str(amount)}|Банкир {str(banker)}'
        )
        await discord_logs.sendLog(
            ctx.guild, 1,
            "BBank",
            uuidToUsername(receiver.user.mc_uuid),
            f'{str(amount)}|Банкир {str(banker)}'
        )

        await discord_logs.sendNotification(
            ctx.guild.get_member(receiver.user.discord_id), 2,
            receiver.name, str(amount)
        )

    @commands.command()
    async def send(self, ctx: commands.Context):
        if mainbool.isAuthor(ctx):
            await ctx.channel.purge(limit=100)
            await ctx.send(
                "Приветствую вас в меню управлением **BeeBank**, здесь представлены основные,"
                " доступные вам функции.", view=buttons.BankButtons()
            )

    @commands.command()
    @commands.has_role(config.getAttr("banker-role-id"))
    async def generate_card(self, ctx: commands.Context, card_id=100001, name="Стандартный счёт", balance="0"):
        if ctx.message.attachments:
            file_formats = ['image/png', 'image/jpeg']
            if ctx.message.attachments[0].content_type in file_formats:
                await ctx.message.attachments[0].save("background.png")
                with open('background.png', "rb") as img_file:
                    my_string = base64.b64encode(img_file.read())
                img = my_string.decode('utf-8')
                await ctx.send(file=generate(img, balance, name, card_id, (255, 255, 255)))
                return
        await ctx.send(file=generate(random_img(), balance, name, card_id, (255, 255, 255)))

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