import os

from database.database import create_db, DATABASE_NAME

# Таблицы
from models.models import User, Card, CardLog


def create_database():
    if not os.path.exists(DATABASE_NAME):
        create_db()
