from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")


# Координаты рабочего места
OFFICE_LAT = 55.700030
OFFICE_LON = 37.623690

# Максимальное расстояние от офиса для чекина
MAX_DISTANCE_METERS = 100