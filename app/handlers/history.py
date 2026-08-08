from aiogram import F, Router
from aiogram.types import Message

from app.database.database import SessionLocal
from app.database.crud import get_user_by_telegram_id
from app.database.models import CheckIn

router = Router()


@router.message(F.text == "📋 История")
async def history(message: Message):
    db = SessionLocal()

    try:
        user = get_user_by_telegram_id(
            db,
            message.from_user.id
        )

        if user is None:
            await message.answer("⛔ Пользователь не найден.")
            return

        checkins = (
            db.query(CheckIn)
            .filter(CheckIn.user_id == user.id)
            .order_by(CheckIn.check_in.desc())
            .limit(10)
            .all()
        )

        if not checkins:
            await message.answer(
                "📋 История пока пустая."
            )
            return

        text = "📋 <b>История рабочих дней</b>\n\n"

        for item in checkins:
            date = item.check_in.strftime("%d.%m.%Y")
            start_time = item.check_in.strftime("%H:%M")

            text += (
                f"📅 <b>{date}</b>\n"
                f"🟢 Начало: <b>{start_time}</b>\n"
            )

            if item.check_out:
                end_time = item.check_out.strftime("%H:%M")

                duration = item.check_out - item.check_in
                total_minutes = int(duration.total_seconds() // 60)

                hours = total_minutes // 60
                minutes = total_minutes % 60

                text += (
                    f"🔴 Конец: <b>{end_time}</b>\n"
                    f"⏱ Продолжительность: <b>{hours} ч {minutes} мин</b>\n\n"
                )
            else:
                text += (
                    "🟡 <b>Рабочий день еще не завершен</b>\n\n"
                )

        await message.answer(text)

    finally:
        db.close()