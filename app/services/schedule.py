from datetime import datetime

from app.database.models import WorkSchedule


def get_today_schedule(db, user_id):
    today = datetime.now().weekday()

    schedule = (
        db.query(WorkSchedule)
        .filter(
            WorkSchedule.user_id == user_id,
            WorkSchedule.weekday == today
        )
        .first()
    )

    return schedule