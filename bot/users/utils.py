import asyncio
import json
import secrets
from pprint import pprint
import aiohttp

from bot.config import settings


def get_refer_id_or_none(command_args: str, user_id: int) -> int:
    """
    Получает идентификатор ссылки или возвращает None, если он недействителен.

    :param command_args: Аргументы команды, которые могут содержать идентификатор.
    :param user_id: Идентификатор пользователя, который отправил команду.
    :return: Идентификатор ссылки или None.
    """
    return int(command_args) if command_args and command_args.isdigit() and int(command_args) > 0 and int(
        command_args) != user_id else None


def generate_token() -> str:
    """
    Генерирует уникальный токен.

    :return: Сгенерированный токен в виде строки.
    """
    return secrets.token_hex(16)  # Генерирует уникальный токен


async def fetch_services() -> dict:
    """
    Получает список доступных услуг из API imeicheck.net.

    :return: Словарь с данными о доступных услугах.
    """
    url = "https://api.imeicheck.net/v1/services"
    api_key = settings.IMEICHECK_TOKEN.get_secret_value()

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()  # Проверка на ошибки
            data = await response.json()  # Получение данных в формате JSON
            return data


async def create_checks(imei: str) -> str:
    """
    Создает проверку IMEI через API imeicheck.net.

    :param imei: IMEI устройства для проверки.
    :return: Строка с результатами проверки.
    """
    url = "https://api.imeicheck.net/v1/checks"
    api_key = settings.IMEICHECK_TOKEN.get_secret_value()

    payload = {
        "deviceId": f"{imei}",
        "serviceId": 12,
    }

    headers = {
        'Authorization': f'Bearer {api_key}',  # Вставьте ваш API ключ
        'Accept-Language': 'en',
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            response.raise_for_status()  # Проверка на ошибки
            data = await response.json()  # Получение данных в формате JSON

            # Преобразование данных в строку для удобного отображения
            out = json.dumps(data).split(',')
            rest = '\n'.join(out)
            return rest


# async def main() -> None:
#     """
#     Основная функция для выполнения асинхронных запросов к API.
#
#     Запускает функции для создания проверок IMEI и выводит результаты.
#     """
#
#     # Пример вызова функции create_checks с IMEI
#     order2 = await create_checks(str(869851059376901))
#
#     # Преобразование результата в JSON и вывод
#     s = json.dumps(order2)
#     pprint(s)
#
#
# if __name__ == '__main__':
#     da = asyncio.run(main())
#     print(da)
