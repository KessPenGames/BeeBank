from database.database import Session
from models.models import User
from utils.mine_converters import usernameToUuid


async def add_user(discord_id: int, mc_uuid: str):
    session = Session()
    user = User(discord_id=discord_id, mc_uuid=mc_uuid)
    session.add(user)
    session.commit()
    session.close()


async def getUser(discord_id: int):
    session = Session()
    user = session.query(User).filter(User.discord_id == discord_id).first()
    session.close()
    if not user:
        return None
    return user


async def getUserByNickname(nickname: str):
    session = Session()
    user = session.query(User).filter(User.mc_uuid == usernameToUuid(nickname)).first()
    session.close()
    if not user:
        return None
    return user


async def updateDiscordId(old_id: int, new_id: int):
    session = Session()
    users = session.query(User).filter(User.discord_id == old_id)
    if users.first():
        users.update({"discord_id": new_id})
        session.commit()
    session.close()


async def updateMCUuid(discord_id: int, mc_uuid: str):
    session = Session()
    users = session.query(User).filter(User.discord_id == discord_id)
    if users.first():
        users.update({"mc_uuid": mc_uuid})
        session.commit()
    session.close()


async def removeUser(discord_id: int):
    session = Session()
    user = await getUser(discord_id)
    if user:
        session.delete(user)
        session.commit()
    session.close()
