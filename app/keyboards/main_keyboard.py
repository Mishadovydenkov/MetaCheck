from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🟢 Чекин")
        ],
        [
            KeyboardButton(text="🔴 Домой")
        ],
        [
            KeyboardButton(text="📋 История")
        ]
    ],
    resize_keyboard=True
)