from aiogram import F
from loguru import logger
from aiogram.types import Message
from aiogram.dispatcher.router import Router

# Создаем роутер для обработки сообщений
echo_router = Router()


@echo_router.message(F.text)
async def cmd_start(message: Message) -> None:
    """
    Обрабатывает текстовые сообщения от пользователя.

    :param message: Объект сообщения от пользователя.
    """
    try:
        # Отправляем ответ пользователю
        await message.reply("Необходимо выбрать команду для начала работы")
    except Exception as e:
        # Логируем ошибку, если что-то пошло не так
        logger.error(f"Ошибка при обработке сообщения от пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")
