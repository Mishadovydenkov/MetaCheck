from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def location_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📍 Отправить геолокацию",
                    request_location=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )