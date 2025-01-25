from pydantic import BaseModel, ConfigDict

class TelegramIDModel(BaseModel):
    """
    Модель для представления идентификатора пользователя Telegram.

    Attributes:
        telegram_id (int): Уникальный идентификатор пользователя в Telegram.
    """
    telegram_id: int

    model_config = ConfigDict(from_attributes=True)


class UserModel(TelegramIDModel):
    """
    Модель для представления пользователя с дополнительной информацией.

    Attributes:
        username (Optional[str]): Имя пользователя в Telegram.
        first_name (Optional[str]): Имя пользователя.
        last_name (Optional[str]): Фамилия пользователя.
        token_id (Optional[str]): Уникальный токен для пользователя.
    """
    username: str | None
    first_name: str | None
    last_name: str | None
    token_id: str | None = None
