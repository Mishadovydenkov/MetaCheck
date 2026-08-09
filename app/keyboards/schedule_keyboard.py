from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def time_keyboard():
    times = [
        "08:00",
        "08:30",
        "08:45",
        "09:00",
        "09:30",
        "17:00",
        "17:30",
        "18:00",
        "18:30",
        "19:00",
    ]

    buttons = []

    for time in times:
        buttons.append(
            [
                KeyboardButton(
                    text=time
                )
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

def employees_keyboard(employees):

    buttons = []

    for employee in employees:
        buttons.append(
            [
                KeyboardButton(
                    text=f"{employee.id} - {employee.full_name}"
                )
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )


def weekdays_keyboard():

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="1 - Понедельник"
                )
            ],
            [
                KeyboardButton(
                    text="2 - Вторник"
                )
            ],
            [
                KeyboardButton(
                    text="3 - Среда"
                )
            ],
            [
                KeyboardButton(
                    text="4 - Четверг"
                )
            ],
            [
                KeyboardButton(
                    text="5 - Пятница"
                )
            ],
            [
                KeyboardButton(
                    text="6 - Суббота"
                )
            ],
            [
                KeyboardButton(
                    text="7 - Воскресенье"
                )
            ],
        ],
        resize_keyboard=True
    )