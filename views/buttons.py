import base64

import disnake
from disnake import ButtonStyle

from bank import user_card, cards_logs
from logs_handlers import discord_logs
from models.models import Card
from views import dropdowns, modals
from messages.history_embed import CardHistoryEmbed
from configs import config

style = ButtonStyle.grey


class BankButtons(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        emoji="<:payment:1026795730276466708>", label="Перевод игроку", style=style, custom_id="bank:payment"
    )
    async def payment(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=True, ephemeral=True)
        options = await getOptions(inter)
        if options:
            await inter.edit_original_message(view=dropdowns.DropdownView(dropdowns.Payment(options)))

    @disnake.ui.button(
        emoji="<:balance:1026796289968578620>", label="Меню карты", style=style, custom_id="bank:card"
    )
    async def balance(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=True, ephemeral=True)
        options = await getOptions(inter)
        if options:
            await inter.edit_original_message(view=dropdowns.DropdownView(dropdowns.Balance(options)))

    @disnake.ui.button(
        emoji="<:history:1026796756987559967>", label="История транзакций", style=style, custom_id="bank:history"
    )
    async def history(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=True, ephemeral=True)
        options = await getOptions(inter)
        if options:
            await inter.edit_original_message(view=dropdowns.DropdownView(dropdowns.History(options)))


class HistoryButtons(disnake.ui.View):
    def __init__(self, isNext: bool, isPrevious: bool, page: int, card_id: int):
        super().__init__(timeout=None)
        self.isNext = isNext
        self.isPrevious = isPrevious
        self.page = page
        self.card_id = card_id

    @disnake.ui.button(
        emoji="<:previous:1028967320778973255>", style=style, custom_id="history:previous"
    )
    async def previous(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if not self.isPrevious:
            button.disabled = not self.isPrevious
            await inter.response.edit_message(view=self)
            return
        che = CardHistoryEmbed(self.card_id)
        page = self.page - 1
        embed = che.getPage(page)
        if embed:
            await inter.response.edit_message(embed=embed, view=HistoryButtons(
                che.isNext(page), che.isPrevious(page), page, self.card_id
            ))

    @disnake.ui.button(
        emoji="<:next:1028967024338157598>", style=style, custom_id="history:next"
    )
    async def next(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if not self.isNext:
            button.disabled = not self.isNext
            await inter.response.edit_message(view=self)
            return
        che = CardHistoryEmbed(self.card_id)
        page = self.page + 1
        embed = che.getPage(page)
        if embed:
            await inter.response.edit_message(embed=embed, view=HistoryButtons(
                che.isNext(page), che.isPrevious(page), page, self.card_id
            ))


class CardButtons(disnake.ui.View):
    file_formats = ['image/png', 'image/jpeg']

    def __init__(self, card_id: int):
        super().__init__(timeout=None)
        self.card_id = card_id

    @disnake.ui.button(
        emoji="<:background:1031045809577410660>", label="Сменить фон", style=style, custom_id="card:change_back"
    )
    async def change_back(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("Запрос принят.", ephemeral=True)
        card: Card = await user_card.getCard(self.card_id)
        await inter.author.send(
            f"Отправьте мне картинку размером **950x595** для смены фона вашей карты **{card.name}**.\n"
            f"Смена фона стоит **10 АР**, если вы не хотите менять фон то напишите **\"Отказ\"**.\n"
            f"Ваш фон не должен содержать: 18+/Шок контент/Запрещенные символики.\n"
            f"В течении 24 часов ваш фон будет установлен на вашу карту."
        )
        user_id = inter.author.id

        def check(m):
            m: disnake.Message = m
            if m.channel.__class__ == disnake.DMChannel:
                if m.author.id == user_id:
                    attach = m.attachments[0].content_type if m.attachments else None
                    return m.content == "Отказ" or attach in self.file_formats

        msg: disnake.Message = await inter.bot.wait_for('message', check=check)
        if msg.content != "Отказ":
            if card.balance >= 10:
                await msg.attachments[0].save("background.png")
                user = inter.bot.get_user(config.getAttr("admin-id"))
                await user.send(str(card.id), file=disnake.File("background.png"), view=BackCheckButtons(card.id, msg.author))
                await user_card.sendMoney(card.id, config.getAttr("grant-card-id"), 10)

                await cards_logs.addLog(2, card.id, config.getAttr("grant-card-id"), '10|Оплата смены фона')
                await cards_logs.addLog(1, config.getAttr("grant-card-id"), card.id, '10|Оплата смены фона')
                await discord_logs.sendNotification(msg.author, 2, card.name, "10")
            else:
                await msg.channel.send("Вам не хватает АР для смены фона.")
        else:
            await msg.channel.send("Вы успешно отменили смену фона.")

    @disnake.ui.button(
        emoji="<:changecolor:1031046587788558346>", label="Сменить цвет текста",
        style=style, custom_id="card:change_color"
    )
    async def change_color(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(modal=modals.ChangeColorModal(self.card_id))

    @disnake.ui.button(
        emoji="<:reopen:1031108414945898578>", label="Переоткрыть карту",
        style=style, custom_id="card:change_id"
    )
    async def change_id(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("Вы хотите переоткрыть карту (Стоимость **8АР**)?",
                                          view=ReopenButtons(self.card_id), ephemeral=True)


class ReopenButtons(disnake.ui.View):
    def __init__(self, card_id: int):
        super().__init__(timeout=None)
        self.card_id = card_id,

    @disnake.ui.button(emoji="✅", style=style, custom_id="reopen:yes")
    async def yes(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(modal=modals.ChangeNameModal(self.card_id))

    @disnake.ui.button(emoji="❌", style=style, custom_id="reopen:no")
    async def no(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.edit_message("Отменено.", view=None)


class BackCheckButtons(disnake.ui.View):
    def __init__(self, card_id: int, user: disnake.User):
        super().__init__(timeout=None)
        self.card_id = card_id,
        self.user = user

    @disnake.ui.button(emoji="✅", style=style, custom_id="check:yes")
    async def yes(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        msg = inter.message
        await msg.attachments[0].save("background.png")
        with open('background.png', "rb") as img_file:
            my_string = base64.b64encode(img_file.read())
        img = my_string.decode('utf-8')
        await user_card.updateImage(self.card_id[0], img)

        card = await user_card.getCard(self.card_id[0])
        await self.user.send(f"Фон вашей карты **{card.name}** был изменён.")

        await msg.delete()

    @disnake.ui.button(emoji="❌", style=style, custom_id="check:no")
    async def no(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        card = await user_card.getCard(self.card_id[0])
        await self.user.send(f"Заявку на смену фона вашей карты **{card.name}** была отменена.\n"
                             f"Причиной этого может служить содержание **Непристойного контента** или другие причины.")

        msg = inter.message
        await msg.delete()


async def getOptions(inter: disnake.MessageInteraction):
    cards = await user_card.getCardsByUserId(inter.author.id)
    if not cards.first():
        await inter.edit_original_message("У вас нет карты! Прийдите в отделение банка "
                                          "на Спавне, чтобы создать банковскую карту.")
        return None
    options = []
    for card in cards:
        option = disnake.SelectOption(
            label=card.id, description=f"Ваша банковская карта {card.name}"
        )
        options.append(option)
    return options
