from sqlalchemy.orm import Session

from app.database.models import User


def get_user_by_telegram_id(db: Session, telegram_id: int):
    return (
        db.query(User)
        .filter(User.telegram_id == telegram_id)
        .first()
    )