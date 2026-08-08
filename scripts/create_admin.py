from app.database.database import SessionLocal
from app.database.models import User

db = SessionLocal()

telegram_id = int(input("Введите Telegram ID администратора: "))
full_name = input("Введите имя администратора: ")
username = input("Введите username (без @, можно оставить пустым): ")

admin = User(
    telegram_id=telegram_id,
    username=username if username else None,
    full_name=full_name,
    role="admin",
    active=True
)

db.add(admin)
db.commit()

print("✅ Администратор успешно создан!")