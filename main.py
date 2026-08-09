import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import BOT_TOKEN
from app.handlers.start import router as start_router
from app.handlers.checkin import router as checkin_router
from app.handlers.checkout import router as checkout_router
from app.handlers.history import router as history_router
from app.services.cleanup import cleanup_old_checkins
from app.handlers.admin_schedule import router as admin_schedule_router
from app.handlers.admin_users import router as admin_users_router

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(checkin_router)
dp.include_router(checkout_router)
dp.include_router(history_router)
dp.include_router(admin_schedule_router)
dp.include_router(admin_users_router)


async def main():
    cleanup_old_checkins()

    print("🤖 MetaCheck Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())