import disnake

from bank import user_card, cards_logs
from configs import config
from exceptions.bank_exception import NotEnoughMoney, CardNotFound
from generators.card_id import generate
from logs_handlers import discord_logs
from models.models import Card
from utils.mine_converters import uuidToUsername
from utils.check import isHex


class PaymentModal(disnake.ui.Modal):
    def __init__(self, card_id) -> None:
        self.card_id = card_id
        components = [
            disnake.ui.TextInput(
                label="Номер карты другого игрока",
                placeholder="Номер карты...",
                custom_id="card",
                style=disnake.TextInputStyle.short,
                min_length=5,
                max_length=6,
                required=True,
            ),
            disnake.ui.TextInput(
                label="Сумма перевода",
                placeholder="Сумма перевода...",
                custom_id="amount",
                style=disnake.TextInputStyle.short,
                min_length=1,
                required=True,
            ),
            disnake.ui.TextInput(
                label="Комментарий перевода",
                placeholder="Комментарий перевода...",
                custom_id="comments",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=1024,
                required=True,
                value="Нет комментариев"
            ),
        ]
        super().__init__(title="Перевод игроку", custom_id="payment", components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        await inter.response.defer(with_message=True, ephemeral=True)
        try:
            sender_card = int(self.card_id)
            receiver_card = int(inter.text_values["card"])
            amount = int(inter.text_values["amount"])
            comments = inter.text_values["comments"]
            if amount > 0:
                await user_card.sendMoney(sender_card, receiver_card, amount)
                await cards_logs.addLog(1, receiver_card, sender_card, str(amount) + '|' + comments)
                await cards_logs.addLog(2, sender_card, receiver_card, str(amount) + '|' + comments)

                sender = await user_card.getCard(sender_card)
                receiver = await user_card.getCard(receiver_card)

                await discord_logs.sendLog(
                    inter.guild, 1,
                    uuidToUsername(receiver.user.mc_uuid),
                    uuidToUsername(sender.user.mc_uuid),
                    str(amount) + '|' + comments
                )
                await discord_logs.sendLog(
                    inter.guild, 2,
                    uuidToUsername(sender.user.mc_uuid),
                    uuidToUsername(receiver.user.mc_uuid),
                    str(amount) + '|' + comments
                )

                await discord_logs.sendNotification(
                    inter.guild.get_member(receiver.user.discord_id), 1,
                    uuidToUsername(sender.user.mc_uuid),
                    str(amount) + '|' + comments
                )
                await discord_logs.sendNotification(
                    inter.guild.get_member(sender.user.discord_id), 2,
                    sender.name, str(amount)
                )

                await inter.edit_original_message(f"Вы успешно перевели **{str(amount)}АР**, "
                                                  f"на карту **{str(receiver_card)}**.")
            else:
                await inter.edit_original_message("Введена неверная сумма для перевода!")
        except CardNotFound as error:
            await inter.edit_original_message(f"Карта **{error.card}** не найдена!")
        except NotEnoughMoney:
            await inter.edit_original_message("Вам не хватает средств для перевода.")
        except ValueError:
            await inter.edit_original_message("Введена неверная сумма для перевода или карта пользователя.")

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        print(error)
        await inter.edit_original_message("Упс, ошибочка.")


class ChangeColorModal(disnake.ui.Modal):
    def __init__(self, card_id) -> None:
        self.card_id = card_id
        components = [
            disnake.ui.TextInput(
                label="Новый цвет текста в HEX",
                placeholder="Цвет текста в HEX...",
                custom_id="hex",
                style=disnake.TextInputStyle.short,
                min_length=6,
                max_length=7,
                required=True
            )
        ]
        super().__init__(title="Смена цвета текста", custom_id="changecolor", components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        await inter.response.defer(with_message=True, ephemeral=True)
        hexColor = str(inter.text_values["hex"]).replace("#", "")
        if isHex('#'+hexColor):
            await user_card.updateColor(self.card_id, hexColor)
            await inter.edit_original_message("Цвет текста успешно изменён.")
        else:
            await inter.edit_original_message("Введён неверный HEX Color формат.")

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        print(error)
        await inter.edit_original_message("Упс, ошибочка.")


class ChangeNameModal(disnake.ui.Modal):
    def __init__(self, card_id) -> None:
        self.card_id = card_id[0]
        components = [
            disnake.ui.TextInput(
                label="Новое название карты",
                placeholder="Новое название карты...",
                custom_id="name",
                style=disnake.TextInputStyle.short,
                max_length=128,
                required=True
            )
        ]
        super().__init__(title="Смена цвета текста", custom_id="changecolor", components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        await inter.response.defer(with_message=True, ephemeral=True)
        name = inter.text_values["name"]
        card: Card = await user_card.getCard(self.card_id)
        if card.balance >= 8:
            await user_card.sendMoney(card.id, config.getAttr("grant-card-id"), 8)
            await user_card.removeMoney(config.getAttr("bank-card-id"), 8)

            await cards_logs.addLog(2, card.id, config.getAttr("grant-card-id"), '8|Оплата переоткрытия карты')
            await cards_logs.addLog(2, config.getAttr("grant-card-id"), card.id, '8|Оплата переоткрытия карты')
            await discord_logs.sendNotification(inter.author, 2, card.name, "8")

            await user_card.updateName(self.card_id, name)
            new_id = generate()
            await user_card.updateCardId(self.card_id, new_id)
            await cards_logs.updateOneCard(self.card_id, new_id)
            await cards_logs.updateTwoCard(self.card_id, new_id)

            await inter.edit_original_message(f"Карта **{card.name}** была переоткрыта.")

            await discord_logs.sendLog(
                inter.guild, 5,
                uuidToUsername(card.user.mc_uuid),
                "None", card.name
            )
        else:
            await inter.edit_original_message("Вам не хватает АР для переоткрытия карты.")

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction) -> None:
        print(error)
        await inter.edit_original_message("Упс, ошибочка.")
