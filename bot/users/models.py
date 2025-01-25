import asyncio
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger
from typing import Optional
from bot.database import Base, async_session_maker


class User(Base):
    """
    Модель пользователя для базы данных.

    Attributes:
        telegram_id (int): Уникальный идентификатор пользователя в Telegram.
        username (Optional[str]): Имя пользователя в Telegram.
        first_name (Optional[str]): Имя пользователя.
        last_name (Optional[str]): Фамилия пользователя.
        token_id (Optional[str]): Уникальный токен для пользователя.
    """

    __tablename__ = 'users'  # Укажите имя таблицы в базе данных

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]]
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    token_id: Mapped[Optional[str]]
