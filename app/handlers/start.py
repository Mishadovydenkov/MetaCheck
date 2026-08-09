from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.database.database import SessionLocal
from app.database.crud import get_user_by_telegram_id
from app.keyboards.main_keyboard import main_keyboard


router = Router()


admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📅 Управление графиком"
            )
        ],
        [
            KeyboardButton(
                text="👤 Добавить сотрудника"
            )
        ]
    ],
    resize_keyboard=True
)


@router.message(CommandStart())
async def start_command(message: Message):
    db = SessionLocal()

    try:
        user = get_user_by_telegram_id(
            db,
            message.from_user.id
        )

        if user is None:
            await message.answer(
                "⛔ <b>Доступ запрещён</b>\n\n"
                "Ваш Telegram ID отсутствует в системе.\n\n"
                f"<code>{message.from_user.id}</code>\n\n"
                "Передайте этот ID администратору."
            )
            return


        if not user.active:
            await message.answer(
                "⏳ Ваша учетная запись еще не активирована."
            )
            return


        # Админская панель
        if user.role == "admin":

            await message.answer(
                f"👋 Привет, {message.from_user.first_name}!\n\n"
                "Вы вошли как администратор MetaCheck.",
                reply_markup=admin_keyboard
            )

            return


        # Обычный сотрудник
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            "Я MetaCheck.\n"
            "Используй кнопку ниже, чтобы начать рабочий день.",
            reply_markup=main_keyboard
        )


    finally:
        db.close()