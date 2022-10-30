import disnake

from bank import user_card
from generators.card_image.card import generate
from models.models import Card
from views import modals, buttons
from messages.history_embed import CardHistoryEmbed


class Payment(disnake.ui.Select):
    def __init__(self, options):
        super().__init__(
            placeholder="Выберите карту",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.send_message(view=DropdownView(PaymentTypes(int(self.values[0]))), ephemeral=True)


class PaymentByNick(disnake.ui.Select):
    def __init__(self, options, card):
        self.card = card
        super().__init__(
            placeholder="Выберите карту",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.send_modal(modal=modals.PaymentModal(self.card, self.values[0]))


class PaymentTypes(disnake.ui.Select):
    def __init__(self, card):
        super().__init__(
            placeholder="Выберите тип перевода",
            min_values=1,
            max_values=1,
            options=[
                disnake.SelectOption(
                    label="По номеру карты", description="Перевести АРы по номеру карты"
                ),
                disnake.SelectOption(
                    label="По никнейму", description="Перевести АРы по никнейму владельца карты"
                ),
                disnake.SelectOption(
                    label="По названию карты", description="Перевести АРы по названию карты"
                ),
            ],
        )
        self.card = card

    async def callback(self, inter: disnake.MessageInteraction):
        if self.values[0] == "По номеру карты":
            await inter.response.send_modal(modal=modals.PaymentModal(self.card))
        elif self.values[0] == "По никнейму":
            await inter.response.send_modal(modal=modals.SearchCardByNick(self.card, True))
        else:
            await inter.response.send_modal(modal=modals.SearchCardByCardName(self.card, True))


class Balance(disnake.ui.Select):
    def __init__(self, options):
        super().__init__(
            placeholder="Выберите карту",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=True, ephemeral=True)
        card: Card = await user_card.getCard(int(self.values[0]))
        color = tuple(int(card.text_color[i:i + 2], 16) for i in (0, 2, 4))
        await inter.edit_original_message(
            view=buttons.CardButtons(int(self.values[0])),
            file=generate(card.background, str(card.balance), card.name, card.id, color)
        )


class History(disnake.ui.Select):
    def __init__(self, options):
        super().__init__(
            placeholder="Выберите карту",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=True, ephemeral=True)
        che = CardHistoryEmbed(int(self.values[0]))
        embed = che.getPage()
        if embed:
            await inter.edit_original_message(embed=embed, view=buttons.HistoryButtons(
                che.isNext(), che.isPrevious(), 1, int(self.values[0])
            ))


class DropdownView(disnake.ui.View):
    def __init__(self, dropdown):
        super().__init__()

        # Add the dropdown to our view object.
        self.add_item(dropdown)
