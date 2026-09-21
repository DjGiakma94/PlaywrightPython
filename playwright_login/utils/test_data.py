from data.users import DEFAULT_USER
from models.user import User


def get_default_user() -> User:
    return User(
        username=DEFAULT_USER["username"],
        password=DEFAULT_USER["password"],
        display_name=DEFAULT_USER["display_name"],
    )
