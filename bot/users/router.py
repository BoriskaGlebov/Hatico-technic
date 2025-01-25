import asyncio
from aiogram import F
from aiogram.filters import CommandObject, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.chat_action import ChatActionSender
from loguru import logger
from aiogram.types import Message
from aiogram.dispatcher.router import Router

from bot.config import bot
from bot.database import connection
from bot.users.dao import UserDAO
from bot.users.keyboards.markup_kb import start_keyboard
from bot.users.schemas import TelegramIDModel, UserModel
from bot.users.utils import generate_token, create_checks


class RegistrationsState(StatesGroup):
    registration = State()
    input_imei = State()
    information_imei = State()


user_router = Router()


@user_router.message(CommandStart())
@connection()
async def cmd_start(message: Message, command: CommandObject, session, state: FSMContext, **kwargs) -> None:
    """
    Обрабатывает команду /start и регистрирует пользователя.

    :param message: Сообщение от пользователя.
    :param command: Объект команды.
    :param session: Сессия базы данных.
    :param state: Контекст состояния FSM.
    """
    try:
        await state.clear()
        user_id = message.from_user.id

        # Проверка существования пользователя в базе данных
        user_info = await UserDAO.find_one_or_none(session=session,
                                                   filters=TelegramIDModel(telegram_id=user_id))

        if not user_info:
            # Если пользователь не найден, добавляем его в базу данных
            values = UserModel(telegram_id=user_id,
                               username=message.from_user.username,
                               first_name=message.from_user.first_name,
                               last_name=message.from_user.last_name)
            await UserDAO.add(session=session, values=values)
        elif user_info.token_id:
            # Если пользователь уже зарегистрирован и имеет токен
            await message.answer(f"👋 Привет, {message.from_user.full_name}! Выберите следующее действие",
                                 reply_markup=start_keyboard(registered=True))
            await state.set_state(RegistrationsState.input_imei)
            return

        # Установка состояния регистрации для нового пользователя
        await state.set_state(RegistrationsState.registration)
        await message.answer(f"👋 Привет, {message.from_user.full_name}! Зарегистрируйтесь для дальнейшей работы",
                             reply_markup=start_keyboard(registered=False))

    except Exception as e:
        logger.error(f"Ошибка при выполнении команды /start для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")


@user_router.message(Command(commands=['registration']))
@user_router.message(F.text.lower().contains('регистрация'), RegistrationsState.registration)
@connection()
async def cmd_registration(message: Message, session, state: FSMContext, command: CommandObject = None,
                           **kwargs) -> None:
    """
    Обрабатывает команду регистрации пользователя.

    :param message: Сообщение от пользователя.
    :param session: Сессия базы данных.
    :param state: Контекст состояния FSM.
    :param command: Объект команды (по умолчанию None).
    """
    try:
        user_id = message.from_user.id

        # Проверка существования пользователя в базе данных
        user_info = await UserDAO.find_one_or_none(session=session,
                                                   filters=TelegramIDModel(telegram_id=user_id))

        token_id = generate_token()  # Генерация токена

        if not user_info:
            # Если пользователь не найден, добавляем его в базу данных с токеном
            values = UserModel(telegram_id=user_id,
                               username=message.from_user.username,
                               first_name=message.from_user.first_name,
                               last_name=message.from_user.last_name,
                               token_id=token_id)
            await UserDAO.add(session=session, values=values)
        elif not user_info.token_id:
            # Если пользователь найден, но не имеет токена - обновляем данные
            values = UserModel(**user_info.to_dict())
            values.token_id = token_id
            await UserDAO.update(session=session, filters=TelegramIDModel(telegram_id=user_id),
                                 values=values)
        elif user_info.token_id:
            # Если пользователь уже зарегистрирован
            await message.answer(f"Пользователь, {message.from_user.full_name} уже зарегистрирован! Нажми кнопку 👇",
                                 reply_markup=start_keyboard(registered=True))
            await state.set_state(RegistrationsState.input_imei)
            return

        # Установка состояния ввода IMEI после успешной регистрации
        await state.set_state(RegistrationsState.input_imei)
        await message.answer(f"Пользователь, {message.from_user.full_name} успешно зарегистрирован! Нажми кнопку 👇",
                             reply_markup=start_keyboard(registered=True))

    except Exception as e:
        logger.error(f"Ошибка при выполнении команды /registration для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")


@user_router.message(Command(commands=['send_imei']))
@user_router.message(F.text.lower().contains('информация по imei'), RegistrationsState.input_imei)
@connection()
async def cmd_input_imei(message: Message, session, state: FSMContext, command: CommandObject = None, **kwargs) -> None:
    """
    Запрашивает у пользователя ввод IMEI.

    :param message: Сообщение от пользователя.
    :param session: Сессия базы данных.
    :param state: Контекст состояния FSM.
    :param command: Объект команды (по умолчанию None).
    """
    try:
        user_id = message.from_user.id

        # Проверка существования пользователя в базе данных и наличия токена
        user_info = await UserDAO.find_one_or_none(session=session,
                                                   filters=TelegramIDModel(telegram_id=user_id))

        if user_info and user_info.token_id:
            await message.answer("Введите IMEI (15 цифр без пробелов).")
        else:
            await message.answer("Необходимо пройти регистрацию!", reply_markup=start_keyboard(registered=False))

        # Установка состояния ввода информации по IMEI
        await state.set_state(RegistrationsState.information_imei)

    except Exception as e:
        logger.error(f"Ошибка при выполнении команды /send_imei для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")


@user_router.message(F.text, RegistrationsState.information_imei)
@connection()
async def cmd_information_imei(message: Message, session, state: FSMContext, command: CommandObject = None,
                               **kwargs) -> None:
    """
    Обрабатывает ввод IMEI и выполняет проверку.

    :param message: Сообщение от пользователя с IMEI.
    :param session: Сессия базы данных.
    :param state: Контекст состояния FSM.
    :param command: Объект команды (по умолчанию None).
    """
    try:
        text = message.text

        if text and (len(text) == 15):
            async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action="typing"):
                await asyncio.sleep(2)  # Эффект набора текста

                res = await create_checks(text)  # Выполнение проверки IMEI

                await message.answer(res)  # Отправка результата пользователю

        else:
            await message.reply("IMEI должен содержать 15 цифр без пробелов. Попробуйте ввести еще раз.")
            return

        await state.clear()  # Очистка состояния после обработки

    except Exception as e:
        logger.error(f"Ошибка при обработке IMEI для пользователя {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте снова позже.")
