from database.database import Session
from models.models import Card

from exceptions.bank_exception import NotEnoughMoney, CardNotFound


async def addCard(discord_id: int, name: str):
    session = Session()
    card = Card(user_id=discord_id, name=name)
    session.add(card)
    session.commit()
    card = session.query(Card).filter(Card.id == card.id).first()
    session.close()
    return card


async def getCard(card_id: int):
    session = Session()
    card = session.query(Card).filter(Card.id == card_id).first()
    session.close()
    if not card:
        raise CardNotFound(card_id)
    return card


def syncGetCard(card_id: int):
    session = Session()
    card = session.query(Card).filter(Card.id == card_id).first()
    session.close()
    if not card:
        raise CardNotFound(card_id)
    return card


async def updateCardId(old_id: int, new_id: int):
    session = Session()
    cards = session.query(Card).filter(Card.id == old_id)
    if cards.first():
        cards.update({"id": new_id})
        session.commit()
    session.close()


async def updateName(card_id: int, name: str):
    session = Session()
    cards = session.query(Card).filter(Card.id == card_id)
    if cards.first():
        cards.update({"name": name})
        session.commit()
    session.close()


async def updateColor(card_id: int, color: str):
    session = Session()
    cards = session.query(Card).filter(Card.id == card_id)
    if cards.first():
        cards.update({"text_color": color})
        session.commit()
    session.close()


async def updateImage(card_id: int, image_bs64: str):
    session = Session()
    cards = session.query(Card).filter(Card.id == card_id)
    if cards.first():
        cards.update({"background": image_bs64})
        session.commit()
    session.close()


async def updateBalance(card_id: int, new_balance: int):
    session = Session()
    cards = session.query(Card).filter(Card.id == card_id)
    if cards.first():
        cards.update({"balance": new_balance})
        session.commit()
    session.close()


async def removeCard(card_id: int):
    session = Session()
    card = await getCard(card_id)
    if card:
        session.delete(card)
        session.commit()
    session.close()


async def getCardsByUserId(user_id: int):
    session = Session()
    cards = session.query(Card).filter(Card.user_id == user_id)
    session.close()
    return cards


async def getCardsByCardName(name: str):
    session = Session()
    cards = session.query(Card).filter(Card.name == name)
    session.close()
    return cards


async def getAllCards():
    session = Session()
    cards = session.query(Card).all()
    session.close()
    return cards


async def addMoney(card_id: int, amount: int):
    card = await getCard(card_id)
    await updateBalance(card_id, card.balance + amount)
    return card


async def removeMoney(card_id: int, amount: int):
    card = await getCard(card_id)
    if amount > card.balance:
        raise NotEnoughMoney(card_id)
    await updateBalance(card_id, card.balance - amount)
    return card


async def sendMoney(sender_card: int, receiver_card: int, amount: int):
    await removeMoney(sender_card, amount)
    await addMoney(receiver_card, amount)
