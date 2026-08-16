from datetime import datetime
import os


def get_current_datetime():
    test_now = os.getenv("TEST_NOW")

    if test_now:
        return datetime.strptime(
            test_now,
            "%Y-%m-%d %H:%M"
        )

    return datetime.now()