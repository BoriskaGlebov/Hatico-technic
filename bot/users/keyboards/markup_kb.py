from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start_keyboard(registered: bool) -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для начала взаимодействия с ботом.

    :param registered: Указывает, зарегистрирован ли пользователь.
    :return: Объект ReplyKeyboardMarkup с кнопками.
    """
    kb = ReplyKeyboardBuilder()

    if not registered:
        # Если пользователь не зарегистрирован, добавляем кнопку регистрации
        kb.button(text="Регистрация")
    else:
        # Если пользователь зарегистрирован, добавляем кнопку для получения информации по IMEI
        kb.button(text="Информация по IMEI")

    kb.adjust(1)  # Настройка количества кнопок в строке
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)
