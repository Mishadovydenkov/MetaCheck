from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message

from app.database.database import SessionLocal
from app.database.models import CheckIn
from app.database.crud import get_user_by_telegram_id

router = Router()


@router.message(F.text == "🔴 Домой")
async def checkout(message: Message):
    db = SessionLocal()

    try:
        user = get_user_by_telegram_id(
            db,
            message.from_user.id
        )

        if user is None:
            await message.answer("⛔ Пользователь не найден.")
            return

        checkin = (
            db.query(CheckIn)
            .filter(
                CheckIn.user_id == user.id,
                CheckIn.check_out == None
            )
            .order_by(CheckIn.check_in.desc())
            .first()
        )

        if checkin is None:
            await message.answer(
                "⚠️ У вас нет активного рабочего дня."
            )
            return

        now = datetime.now()

        checkin.check_out = now

        db.commit()

        await message.answer(
            f"""
🔴 <b>ЧЕКАУТ</b>

👤 <b>{message.from_user.full_name}</b>

📅 {now.strftime('%d.%m.%Y')}
🕒 {now.strftime('%H:%M:%S')}

🏠 Рабочий день завершен!
"""
        )

    finally:
        db.close()