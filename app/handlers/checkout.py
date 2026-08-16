from aiogram import F, Router
from aiogram.types import Message

from app.database.database import SessionLocal
from app.database.models import CheckIn
from app.database.crud import get_user_by_telegram_id
from app.services.schedule import get_today_schedule
from app.services.time import get_current_datetime

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
            await message.answer(
                "⛔ Пользователь не найден."
            )
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

        schedule = get_today_schedule(
            db,
            user.id
        )

        if schedule is None:
            await message.answer(
                "⚠️ Не удалось найти график на сегодня."
            )
            return

        now = get_current_datetime()

        checkin.check_out = now

        shift_end = now.replace(
            hour=schedule.end_time.hour,
            minute=schedule.end_time.minute,
            second=0,
            microsecond=0
        )

        early_leave_minutes = 0
        overtime_minutes = 0

        # Ушел раньше окончания смены
        if now < shift_end:
            early_leave_minutes = int(
                (shift_end - now).total_seconds() // 60
            )

        # Остался после окончания смены
        elif now > shift_end:
            overtime_minutes = int(
                (now - shift_end).total_seconds() // 60
            )

        checkin.early_leave_minutes = early_leave_minutes
        checkin.overtime_minutes = overtime_minutes

        db.commit()

        if early_leave_minutes > 0:

            status_text = (
                f"⚠️ Ранний уход: "
                f"<b>{early_leave_minutes} мин.</b>"
            )

        elif overtime_minutes > 0:

            status_text = (
                f"⏱ Переработка: "
                f"<b>{overtime_minutes} мин.</b>"
            )

        else:

            status_text = (
                "✅ Уход по графику"
            )

        await message.answer(
            f"""
🔴 <b>ЧЕКАУТ</b>

👤 <b>{message.from_user.full_name}</b>

📅 {now.strftime('%d.%m.%Y')}
🕒 {now.strftime('%H:%M:%S')}

⏰ График: <b>{schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}</b>

{status_text}

🏠 Рабочий день завершен!
"""
        )

    finally:
        db.close()