from datetime import datetime

import disnake

from bank import cards_logs
from models.models import CardLog


class CardHistoryEmbed:
    def __init__(self, card_id: int):
        self.logs = sorted(cards_logs.syncGetLogsByCard(card_id), key=lambda t: datetime
                           .strptime(str(t.date), '%Y-%m-%d %H:%M:%S'), reverse=True
                           )
        self.max_page = getMaxPage(len(self.logs) / 5, len(self.logs) // 5)

    def isNext(self, page: int = 1):
        return False if page >= self.max_page else True

    def isPrevious(self, page: int = 1):
        return False if page <= 1 else True

    def getPage(self, page: int = 1):
        if not self.logs:
            return disnake.Embed(
                title="История транзакций 0/0",
                description="У вас нет истории транзакций!",
                color=3092790
            )
        if page > self.max_page:
            return None
        embed = disnake.Embed(
            title=f"История транзакций {page}/{self.max_page}",
            color=3092790
        )
        for i in range((page * 5) - 5, page * 5):
            try:
                log: CardLog = self.logs[i]
                typeLog = "(+)" if log.log_type == 1 else "(-)"
                balance, comments = log.other_data.split("|")
                try:
                    embed.add_field(
                        name=f"{typeLog} {log.two_card.user} Сумма: {balance}АР",
                        value=f"{comments}\nДата: {log.date}",
                        inline=False
                    )
                except AttributeError:
                    embed.add_field(
                        name=f"{typeLog} None Сумма: {balance}АР",
                        value=f"{comments}\nДата: {log.date}",
                        inline=False
                    )
            except IndexError:
                continue
        return embed


def getMaxPage(one, two):
    return two + 1 if one > two else two
