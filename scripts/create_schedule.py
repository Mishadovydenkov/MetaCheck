from datetime import time

from app.database.database import SessionLocal
from app.database.models import WorkSchedule


db = SessionLocal()


user_id = 1

schedule = [
    WorkSchedule(
        user_id=user_id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(18, 0)
    ),
    WorkSchedule(
        user_id=user_id,
        weekday=1,
        start_time=time(9, 0),
        end_time=time(18, 0)
    ),
    WorkSchedule(
        user_id=user_id,
        weekday=2,
        start_time=time(9, 0),
        end_time=time(18, 0)
    ),
    WorkSchedule(
        user_id=user_id,
        weekday=3,
        start_time=time(9, 0),
        end_time=time(18, 0)
    ),
    WorkSchedule(
        user_id=user_id,
        weekday=4,
        start_time=time(9, 0),
        end_time=time(18, 0)
    ),
]


db.add_all(schedule)
db.commit()

db.close()

print("✅ График создан")