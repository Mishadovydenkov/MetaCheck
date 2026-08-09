from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
    Float,
)

from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    telegram_id = Column(
        Integer,
        unique=True,
        nullable=False
    )

    username = Column(String)

    full_name = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        default="employee"
    )

    active = Column(
        Boolean,
        default=False
    )


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    check_in = Column(
        DateTime,
        default=datetime.now
    )

    check_out = Column(
        DateTime,
        nullable=True
    )

    late_minutes = Column(
        Integer,
        default=0,
        nullable=False
    )

    late_reason = Column(
        String,
        nullable=True
    )

    # Новое: координаты сотрудника при чекине
    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    user = relationship("User")


class WorkSchedule(Base):
    __tablename__ = "work_schedules"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    weekday = Column(
        Integer,
        nullable=False
    )

    start_time = Column(
        Time,
        nullable=False
    )

    end_time = Column(
        Time,
        nullable=False
    )

    user = relationship("User")