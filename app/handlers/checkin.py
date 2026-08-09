from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.database.database import SessionLocal
from app.database.models import CheckIn
from app.database.crud import get_user_by_telegram_id
from app.services.schedule import get_today_schedule
from app.keyboards.location_keyboard import location_keyboard


router = Router()


class CheckinState(StatesGroup):
    waiting_location = State()


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


        if now > late_limit:

            late_minutes = int(
                (now - shift_start)
                .total_seconds() // 60
            )

            pending_late[message.from_user.id] = {
                "user_id": user.id,
                "check_in": now,
                "late_minutes": late_minutes
            }


            await message.answer(
                f"⚠️ <b>Вы опоздали на {late_minutes} мин.</b>\n\n"
                "Сначала отправьте геолокацию.\n"
                "После проверки укажите причину опоздания."
            )

        else:

            await state.set_state(
                CheckinState.waiting_location
            )


            await message.answer(
                "📍 Для начала рабочего дня отправьте вашу геолокацию.",
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


    await state.update_data(
        latitude=latitude,
        longitude=longitude
    )


    await message.answer(
        "📍 Геолокация получена!\n\n"
        f"Широта: <code>{latitude}</code>\n"
        f"Долгота: <code>{longitude}</code>\n\n"
        "⏳ Следующий шаг — проверка расстояния до рабочего места."
    )


    await state.clear()