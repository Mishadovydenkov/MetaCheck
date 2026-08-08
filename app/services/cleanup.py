from datetime import datetime, timedelta

from app.database.database import SessionLocal
from app.database.models import CheckIn


def cleanup_old_checkins():
    db = SessionLocal()

    try:
        limit_date = datetime.now() - timedelta(days=35)

        deleted = (
            db.query(CheckIn)
            .filter(CheckIn.check_in < limit_date)
            .delete()
        )

        db.commit()

        if deleted:
            print(f"🧹 Удалено старых записей: {deleted}")

    finally:
        db.close()