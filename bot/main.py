import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger

from bot.config import bot, admins, dp
from bot.echo.router import echo_router
from bot.users.router import user_router


async def set_commands() -> None:
    """
    Настраивает командное меню (дефолтное для всех пользователей).
    """
    commands = [
        BotCommand(command='start', description='Старт'),
        BotCommand(command='registration', description='Регистрация'),
        BotCommand(command='send_imei', description='Отправить IMEI')
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def set_description(bot: Bot) -> None:
    """
    Устанавливает описание бота.

    :param bot: Экземпляр бота.
    """
    inf = await bot.get_me()
    await bot.set_my_description(f'{inf.first_name} приветствует тебя!\n'
                                 f'Этот 🤖 БОТ занимается поиском\n'
                                 f'информации об устройстве по его IMEI')


async def start_bot(bot: Bot) -> None:
    """
    Функция, которая выполнится, когда бот запустится.

    :param bot: Экземпляр бота.
    """
    await set_commands()
    await set_description(bot)

    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Я запущен🥳.')
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение администратору {admin_id}: {e}")

    logger.info("Бот успешно запущен.")


async def stop_bot() -> None:
    """
    Функция, которая выполнится, когда бот завершит свою работу.
    """
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение администратору при остановке: {e}")

    logger.error("Бот остановлен!")


async def main() -> None:
    """
    Основная функция для запуска бота.
    Регистрация роутеров и функций.
    """

    # Регистрация роутеров
    dp.include_router(user_router)
    dp.include_router(echo_router)

    # Регистрация функций
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    # Запуск бота в режиме long polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
