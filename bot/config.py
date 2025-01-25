import os
import sys
from typing import List
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# Использую разные .env файлы для разработки и для деплоя
env_file_local: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
env_file_docker: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env.docker")


class Settings(BaseSettings):
    """
    Схема с конфигурацией приложения.

    Атрибуты:
        BOT_TOKEN (str): Токен бота.
        ADMIN_IDS (List[int]): Список идентификаторов администраторов.
        DB_USER (str): Пользователь базы данных.
        DB_PASSWORD (SecretStr): Пароль базы данных (секрет).
        DB_HOST (str): Хост базы данных.
        DB_PORT (int): Порт базы данных.
        DB_NAME (str): Имя основной базы данных.
        PYTHONPATH (str): Путь к Python.

    Методы:
        get_db_url() -> str: Возвращает URL для основной базы данных.
    """

    BOT_TOKEN: str
    ADMIN_IDS: List[int]

    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    PYTHONPATH: str

    model_config = SettingsConfigDict(extra="ignore")

    def get_db_url(self) -> str:
        """
        Получает URL для основной базы данных.

        :return: URL базы данных в формате строки.
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


def get_settings() -> Settings:
    """
    Загружает настройки из файла окружения.

    :return: Экземпляр класса Settings с загруженными параметрами.

    :raises RuntimeError: Если возникают ошибки валидации при загрузке настроек.
    """
    env_file = env_file_docker if os.getenv("ENV") == "docker" else env_file_local
    try:
        return Settings(_env_file=env_file)
    except ValidationError as e:
        # Извлечение сообщений об ошибках с указанием полей
        error_messages = []
        for error in e.errors():
            field = error["loc"]  # Получаем местоположение ошибки
            message = error["msg"]  # Получаем сообщение об ошибке
            error_messages.append(f"Field '{field[-1]}' error: {message}")  # Указываем поле и сообщение

        raise RuntimeError(f"Validation errors: {', '.join(error_messages)}")


try:
    # Получаем параметры для загрузки переменных среды
    settings = get_settings()
except RuntimeError as e:
    print(e)

# Инициализируем бота и диспетчер
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
admins = settings.ADMIN_IDS
# Получение URL базы данных
database_url = settings.get_db_url()

# Удаляем все существующие обработчики
logger.remove()

# Настройка логирования
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> - "
           "<level>{level:^8}</level> - "
           "<cyan>{name}</cyan>:<magenta>{line}</magenta> - "
           "<yellow>{function}</yellow> - "
           "<white>{message}</white> <magenta>{extra[user]:^10}</magenta>",
)

# Конфигурация логгера с дополнительными полями
logger.configure(extra={"ip": "", "user": ""})
logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "file.log"),
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {name}:{line} - {function} - {message} {extra[user]}",
    rotation="1 day",
    retention="7 days",
    backtrace=True,
    diagnose=True,
)

# Теперь вы можете использовать logger в других модулях
# Явный экспорт для того чтобы mypy не ругался
__all__ = ["logger"]

if __name__ == '__main__':
    print(settings)
    print(database_url)
    logger.info('test_info')
    logger.bind(user="BORIS").error('test_error')
    print(admins)
