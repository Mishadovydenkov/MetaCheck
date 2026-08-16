from app.database.models import WorkSchedule
from app.services.time import get_current_datetime


def get_today_schedule(db, user_id):
    today = get_current_datetime().weekday()

    schedule = (
        db.query(WorkSchedule)
        .filter(
            WorkSchedule.user_id == user_id,
            WorkSchedule.weekday == today
        )
        .first()
    )

    return schedule