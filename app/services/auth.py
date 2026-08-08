ALLOWED_USERS = {
    331770944, 438844715, 778243455
}


def is_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS