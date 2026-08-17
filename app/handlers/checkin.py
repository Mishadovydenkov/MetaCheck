from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.database.database import SessionLocal
from app.database.models import CheckIn
from app.database.crud import get_user_by_telegram_id
from app.services.schedule import get_today_schedule
from app.services.geolocation import calculate_distance
from app.services.time import get_current_datetime
from app.keyboards.location_keyboard import location_keyboard
from app.keyboards.main_keyboard import main_keyboard
from app.config import (
    OFFICE_LAT,
    OFFICE_LON,
    MAX_DISTANCE_METERS
)

router = Router()


class CheckinState(StatesGroup):
    waiting_location = State()
    waiting_late_reason = State()


pending_late = {}


@router.message(F.text == "🟢 Чекин")
async def checkin(
    message: Message,
    state: FSMContext
):
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

        now = get_current_datetime()

        # Смена еще не началась
        if now.time() < schedule.start_time:
            await message.answer(
                f"⛔ Рабочий день еще не начался.\n\n"
                f"Начало смены: "
                f"<b>{schedule.start_time.strftime('%H:%M')}</b>"
            )
            return

        # Смена уже закончилась
        if now.time() >= schedule.end_time:
            await message.answer(
                f"⛔ Рабочий день уже закончился.\n\n"
                f"График на сегодня: "
                f"<b>{schedule.start_time.strftime('%H:%M')} - "
                f"{schedule.end_time.strftime('%H:%M')}</b>",
                reply_markup=main_keyboard
            )
            return

        shift_start = datetime.combine(
            now.date(),
            schedule.start_time
        )

        # Первые 20 минут после начала смены
        # считаются временем без опоздания.
        #
        # Например:
        # 08:45 - 09:05 → без опоздания
        late_limit = shift_start + timedelta(minutes=20)

        if now > late_limit:
            late_minutes = int(
                (now - shift_start).total_seconds() // 60
            )

            pending_late[message.from_user.id] = {
                "user_id": user.id,
                "check_in": now,
                "late_minutes": late_minutes
            }

        else:
            pending_late.pop(
                message.from_user.id,
                None
            )

        await state.set_state(
            CheckinState.waiting_location
        )

        await message.answer(
            "📍 Для начала рабочего дня отправьте "
            "вашу геолокацию.",
            reply_markup=location_keyboard()
        )

    finally:
        db.close()


@router.message(
    CheckinState.waiting_location,
    F.location
)
async def get_location(
    message: Message,
    state: FSMContext
):
    latitude = message.location.latitude
    longitude = message.location.longitude

    distance = calculate_distance(
        latitude,
        longitude,
        OFFICE_LAT,
        OFFICE_LON
    )

    # Сотрудник находится слишком далеко
    if distance > MAX_DISTANCE_METERS:
        await message.answer(
            f"❌ <b>Вы находитесь слишком далеко "
            f"от рабочего места.</b>\n\n"
            f"📍 Расстояние до офиса: "
            f"<b>{distance:.0f} м</b>\n"
            f"📏 Допустимое расстояние: "
            f"<b>{MAX_DISTANCE_METERS} м</b>\n\n"
            "Чекин не выполнен.",
            reply_markup=main_keyboard
        )

        await state.clear()

        pending_late.pop(
            message.from_user.id,
            None
        )

        return

    data = pending_late.get(
        message.from_user.id
    )

    db = SessionLocal()

    try:
        # Сотрудник пришел вовремя
        if data is None:
            now = get_current_datetime()

            checkin_record = CheckIn(
                user_id=await get_user_id(
                    message.from_user.id,
                    db
                ),
                check_in=now,
                late_minutes=0,
                late_reason=None
            )

            db.add(checkin_record)
            db.commit()

            await message.answer(
                "🟢 <b>ЧЕКИН ВЫПОЛНЕН!</b>\n\n"
                f"👤 {message.from_user.full_name}\n"
                f"📅 {now.strftime('%d.%m.%Y')}\n"
                f"🕒 {now.strftime('%H:%M:%S')}\n"
                f"📍 Расстояние до офиса: "
                f"{distance:.0f} м\n\n"
                "✅ Рабочий день начат!",
                reply_markup=main_keyboard
            )

            await state.clear()
            return

        # Сотрудник опоздал
        await state.set_state(
            CheckinState.waiting_late_reason
        )

        await message.answer(
            f"📍 Геолокация подтверждена.\n"
            f"Расстояние до офиса: "
            f"<b>{distance:.0f} м</b>\n\n"
            f"⚠️ Опоздание: "
            f"<b>{data['late_minutes']} мин.</b>\n\n"
            "📝 Напишите причину опоздания."
        )

    finally:
        db.close()


@router.message(
    CheckinState.waiting_late_reason
)
async def late_reason(
    message: Message,
    state: FSMContext
):
    data = pending_late.pop(
        message.from_user.id,
        None
    )

    if data is None:
        await message.answer(
            "❌ Данные о чекине не найдены. "
            "Попробуйте выполнить чекин заново.",
            reply_markup=main_keyboard
        )

        await state.clear()
        return

    db = SessionLocal()

    try:
        checkin_record = CheckIn(
            user_id=data["user_id"],
            check_in=data["check_in"],
            late_minutes=data["late_minutes"],
            late_reason=message.text
        )

        db.add(checkin_record)
        db.commit()

        await message.answer(
            "🟢 <b>ЧЕКИН ВЫПОЛНЕН!</b>\n\n"
            f"📅 {data['check_in'].strftime('%d.%m.%Y')}\n"
            f"🕒 {data['check_in'].strftime('%H:%M:%S')}\n\n"
            f"⚠️ Опоздание: "
            f"<b>{data['late_minutes']} мин.</b>\n"
            f"📝 Причина: {message.text}\n\n"
            "✅ Рабочий день начат!",
            reply_markup=main_keyboard
        )

    finally:
        db.close()
        await state.clear()


async def get_user_id(
    telegram_id: int,
    db
):
    user = get_user_by_telegram_id(
        db,
        telegram_id
    )

    return user.id