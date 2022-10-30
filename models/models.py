from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base
from utils.mine_converters import uuidToUsername
from generators.card_id import generate
from generators.card_image.card import random_img


class User(Base):
    __tablename__ = 'bank_user'

    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer, unique=True)
    mc_uuid = Column(String, unique=True)
    date = Column(DateTime(timezone=True), server_default=func.now())

    cards = relationship('Card', back_populates="user", cascade="all, delete-orphan",
                         primaryjoin="User.discord_id == Card.user_id")

    def __init__(self, discord_id: int, mc_uuid: str):
        self.discord_id = discord_id
        self.mc_uuid = mc_uuid

    def __repr__(self):
        return uuidToUsername(self.mc_uuid)


class Card(Base):
    __tablename__ = 'user_card'

    id = Column(Integer, unique=True, primary_key=True)
    name = Column(String)
    background = Column(Text, default=random_img())
    text_color = Column(String, default="ffffff")
    balance = Column(Integer, default=0)
    votes = Column(Integer, default=0)
    date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('bank_user.discord_id', ondelete='CASCADE'))

    user = relationship('User', back_populates="cards", foreign_keys='Card.user_id',
                        passive_deletes=True, lazy='joined')

    def __init__(self, user_id: int, name: str):
        self.user_id = user_id
        self.name = name
        self.id = generate()

    def __repr__(self):
        return str(self.id)


class CardLog(Base):
    __tablename__ = 'cards_logs'

    id = Column(Integer, primary_key=True)
    log_type = Column(Integer)
    other_data = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now())
    one_card_id = Column(Integer, ForeignKey('user_card.id', ondelete='CASCADE'))
    two_card_id = Column(Integer, ForeignKey('user_card.id', ondelete='CASCADE'))

    one_card = relationship('Card', foreign_keys='CardLog.one_card_id',
                            passive_deletes=True, lazy='joined')
    two_card = relationship('Card', foreign_keys='CardLog.two_card_id',
                            passive_deletes=True, lazy='joined')

    def __init__(self, log_type: int, sender_card: int, receiver_card: int, other_data: str):
        self.log_type = log_type
        self.other_data = other_data
        self.one_card_id = sender_card
        self.two_card_id = receiver_card

    def __repr__(self):
        return str(self.id)
