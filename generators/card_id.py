import random

from exceptions.bank_exception import CardNotFound


def generate():
    from bank import user_card
    while True:
        rand = random.randint(100000, 999999)
        try:
            user_card.syncGetCard(rand)
            continue
        except CardNotFound:
            return rand
