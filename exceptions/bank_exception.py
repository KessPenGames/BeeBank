from disnake.ext.commands.errors import CommandError


class NotEnoughMoney(CommandError):
    def __init__(self, card):
        self.card = card

    def __str__(self):
        return f"On the card {self.card} insufficient money."


class CardNotFound(CommandError):
    def __init__(self, card):
        self.card = card

    def __str__(self):
        return f"Card {self.card} not found."
