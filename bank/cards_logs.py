from database.database import Session
from models.models import CardLog


async def addLog(log_type: int, one_card_id: int, two_card_id: int, other_data: str):
    session = Session()
    log = CardLog(log_type=log_type, sender_card=one_card_id, receiver_card=two_card_id, other_data=other_data)
    session.add(log)
    session.commit()
    session.close()


async def getLogsByCard(card_id: int, isOneCard: bool = True):
    session = Session()
    filtering = CardLog.one_card_id if isOneCard else CardLog.two_card_id
    logs = session.query(CardLog).filter(filtering == card_id)
    session.close()
    return logsToList(logs)


def syncGetLogsByCard(card_id: int, isOneCard: bool = True):
    session = Session()
    filtering = CardLog.one_card_id if isOneCard else CardLog.two_card_id
    logs = session.query(CardLog).filter(filtering == card_id)
    session.close()
    return logsToList(logs)


async def removeAllLogsByCard(card_id: int, isOneCard: bool = True):
    session = Session()
    logs = await getLogsByCard(card_id, isOneCard)
    if logs:
        for log in logs:
            session.delete(log)
            session.commit()
    session.close()


def logsToList(logs):
    new_logs = []
    for log in logs:
        new_logs.append(log)
    return new_logs


async def updateOneCard(old_id: int, new_id: int):
    session = Session()
    cards = session.query(CardLog).filter(CardLog.one_card_id == old_id)
    if cards.first():
        cards.update({"one_card_id": new_id})
        session.commit()
    session.close()


async def updateTwoCard(old_id: int, new_id: int):
    session = Session()
    cards = session.query(CardLog).filter(CardLog.two_card_id == old_id)
    if cards.first():
        cards.update({"two_card_id": new_id})
        session.commit()
    session.close()
