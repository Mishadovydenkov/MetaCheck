from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.database.database import SessionLocal
from app.database.models import User

router = Router()


class AddEmployeeState(StatesGroup):
    waiting_telegram_id = State()
    waiting_full_name = State()


@router.message(F.text == "👤 Добавить сотрудника")
async def start_add_employee(
    message: Message,
    state: FSMContext
):
    db = SessionLocal()

    try:
        admin = (
            db.query(User)
            .filter(
                User.telegram_id == message.from_user.id
            )
            .first()
        )

        if admin is None or admin.role != "admin":
            await message.answer(
                "⛔ У вас нет прав администратора."
            )
            return

    finally:
        db.close()

    await state.set_state(
        AddEmployeeState.waiting_telegram_id
    )

    await message.answer(
        "👤 <b>Добавление сотрудника</b>\n\n"
        "Введите Telegram ID сотрудника.\n\n"
        "Например:\n"
        "<code>123456789</code>"
    )


@router.message(AddEmployeeState.waiting_telegram_id)
async def get_telegram_id(
    message: Message,
    state: FSMContext
):
    if not message.text.isdigit():
        await message.answer(
            "❌ Telegram ID должен содержать только цифры.\n\n"
            "Попробуйте ещё раз."
        )
        return

    telegram_id = int(message.text)

    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(
                User.telegram_id == telegram_id
            )
            .first()
        )

        if existing_user:
            await message.answer(
                "⚠️ Пользователь с таким Telegram ID "
                "уже существует."
            )
            return

    finally:
        db.close()

    await state.update_data(
        telegram_id=telegram_id
    )

    await state.set_state(
        AddEmployeeState.waiting_full_name
    )

    await message.answer(
        "Теперь введите <b>ФИО сотрудника</b>."
    )


@router.message(AddEmployeeState.waiting_full_name)
async def get_full_name(
    message: Message,
    state: FSMContext
):
    full_name = message.text.strip()

    if len(full_name) < 2:
        await message.answer(
            "❌ ФИО слишком короткое.\n\n"
            "Введите ФИО ещё раз."
        )
        return

    data = await state.get_data()

    telegram_id = data["telegram_id"]

    db = SessionLocal()

    try:
        employee = User(
            telegram_id=telegram_id,
            username=None,
            full_name=full_name,
            role="employee",
            active=True
        )

        db.add(employee)
        db.commit()

        await message.answer(
            "✅ <b>Сотрудник добавлен!</b>\n\n"
            f"👤 {full_name}\n"
            f"🆔 Telegram ID: <code>{telegram_id}</code>\n"
            "🔵 Статус: активен\n"
            "👨‍💼 Роль: сотрудник"
        )

    finally:
        db.close()
        await state.clear()