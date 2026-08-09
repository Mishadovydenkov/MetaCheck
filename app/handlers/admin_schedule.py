from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.database.database import SessionLocal
from app.database.models import User, WorkSchedule

from app.keyboards.schedule_keyboard import (
    employees_keyboard,
    weekdays_keyboard,
    time_keyboard
)


router = Router()


class ScheduleState(StatesGroup):
    waiting_employee = State()
    waiting_weekday = State()
    waiting_start_time = State()
    waiting_end_time = State()


weekdays = {
    "1": "Понедельник",
    "2": "Вторник",
    "3": "Среда",
    "4": "Четверг",
    "5": "Пятница",
    "6": "Суббота",
    "7": "Воскресенье",
}


@router.message(F.text == "📅 Управление графиком")
async def manage_schedule(
    message: Message,
    state: FSMContext
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.telegram_id == message.from_user.id
            )
            .first()
        )

        if user is None or user.role != "admin":
            await message.answer(
                "⛔ У вас нет прав администратора."
            )
            return


        employees = (
            db.query(User)
            .filter(
                User.role == "employee",
                User.active == True
            )
            .all()
        )


        if not employees:
            await message.answer(
                "👥 Активных сотрудников пока нет."
            )
            return


        await state.set_state(
            ScheduleState.waiting_employee
        )


        await message.answer(
            "👤 Выберите сотрудника:",
            reply_markup=employees_keyboard(employees)
        )


    finally:
        db.close()



@router.message(ScheduleState.waiting_employee)
async def choose_employee(
    message: Message,
    state: FSMContext
):

    try:
        employee_id = int(
            message.text.split(" - ")[0]
        )

    except ValueError:

        await message.answer(
            "❌ Выберите сотрудника кнопкой."
        )
        return


    await state.update_data(
        employee_id=employee_id
    )


    await state.set_state(
        ScheduleState.waiting_weekday
    )


    await message.answer(
        "📅 Выберите день недели:",
        reply_markup=weekdays_keyboard()
    )



@router.message(ScheduleState.waiting_weekday)
async def choose_day(
    message: Message,
    state: FSMContext
):

    try:

        weekday = int(
            message.text.split(" - ")[0]
        )

    except ValueError:

        await message.answer(
            "❌ Выберите день кнопкой."
        )
        return


    await state.update_data(
        weekday=weekday
    )


    await state.set_state(
        ScheduleState.waiting_start_time
    )


    await message.answer(
        "⏰ Выберите время начала смены:",
        reply_markup=time_keyboard()
    )



@router.message(ScheduleState.waiting_start_time)
async def set_start_time(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        start_time=message.text
    )


    await state.set_state(
        ScheduleState.waiting_end_time
    )


    await message.answer(
        "⏰ Выберите время окончания смены:",
        reply_markup=time_keyboard()
    )



@router.message(ScheduleState.waiting_end_time)
async def set_end_time(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    print("FSM DATA:", data)


    db = SessionLocal()


    try:

        start = datetime.strptime(
            data["start_time"],
            "%H:%M"
        ).time()


        end = datetime.strptime(
            message.text,
            "%H:%M"
        ).time()



        schedule = WorkSchedule(
            user_id=data["employee_id"],
            weekday=data["weekday"],
            start_time=start,
            end_time=end
        )


        db.add(schedule)
        db.commit()



        await message.answer(
            "✅ <b>График добавлен!</b>\n\n"
            f"👤 ID сотрудника: {data['employee_id']}\n"
            f"📅 День: {weekdays[str(data['weekday'])]}\n"
            f"⏰ {data['start_time']} - {message.text}"
        )


    finally:

        db.close()
        await state.clear()