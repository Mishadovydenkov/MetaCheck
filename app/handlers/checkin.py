from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.types import Message

from app.database.database import SessionLocal
from app.database.models import CheckIn
from app.database.crud import get_user_by_telegram_id
from app.services.schedule import get_today_schedule

router = Router()

pending_late = {}


@router.message(F.text == "🟢 Чекин")
async def checkin(message: Message):
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

        schedule = get_today_schedule(
            db,
            user.id
        )

        if schedule is None:
            await message.answer(
                "⛔ Сегодня у вас нет рабочего графика."
            )
            return

        active_checkin = (
            db.query(CheckIn)
            .filter(
                CheckIn.user_id == user.id,
                CheckIn.check_out == None
            )
            .first()
        )

        if active_checkin:
            await message.answer(
                "⚠️ <b>Рабочий день уже начат.</b>\n\n"
                "Сначала выполните 🔴 Домой."
            )
            return

        now = datetime.now()

        if now.time() < schedule.start_time:
            await message.answer(
                f"⛔ Рабочий день еще не начался.\n\n"
                f"Начало смены: "
                f"<b>{schedule.start_time.strftime('%H:%M')}</b>"
            )
            return

        shift_start = datetime.combine(
            now.date(),
            schedule.start_time
        )

        late_limit = shift_start + timedelta(minutes=20)

        # Время с 08:45 до 09:05 включительно — без опоздания
        if now <= late_limit:
            checkin = CheckIn(
                user_id=user.id,
                check_in=now,
                late_minutes=0,
                late_reason=None
            )

            db.add(checkin)
            db.commit()

            await message.answer(
                f"""
🟢 <b>ЧЕКИН</b>

👤 <b>{message.from_user.full_name}</b>

📅 {now.strftime('%d.%m.%Y')}
🕒 {now.strftime('%H:%M:%S')}

✅ Рабочий день начат!
"""
            )

            return

        # Опоздание
        late_minutes = int(
            (now - shift_start).total_seconds() // 60
        )

        pending_late[message.from_user.id] = {
            "user_id": user.id,
            "check_in": now,
            "late_minutes": late_minutes
        }

        await message.answer(
            f"⚠️ <b>Вы опоздали на {late_minutes} мин.</b>\n\n"
            "Пожалуйста, напишите причину опоздания."
        )

    finally:
        db.close()


@router.message(
    lambda message: message.from_user.id in pending_late
)
async def late_reason(message: Message):
    data = pending_late.pop(message.from_user.id)

    db = SessionLocal()

    try:
        checkin = CheckIn(
            user_id=data["user_id"],
            check_in=data["check_in"],
            late_minutes=data["late_minutes"],
            late_reason=message.text
        )

        db.add(checkin)
        db.commit()

        await message.answer(
            f"""
🟢 <b>ЧЕКИН</b>

📅 {data["check_in"].strftime("%d.%m.%Y")}
🕒 {data["check_in"].strftime("%H:%M:%S")}

⚠️ Опоздание: <b>{data["late_minutes"]} мин.</b>
📝 Причина: <b>{message.text}</b>

✅ Рабочий день начат!
"""
        )

    finally:
        db.close()