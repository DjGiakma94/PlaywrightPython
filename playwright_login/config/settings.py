import os
from enum import Enum


def _load_dotenv(path=".env"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if "=" not in s:
                    continue
                k, v = s.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v
    except FileNotFoundError:
        pass


_load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


class Env(Enum):
    USERNAME = "PLAYWRIGHT_USERNAME"
    PASSWORD = "PLAYWRIGHT_PASSWORD"
    DISPLAY_NAME = "PLAYWRIGHT_DISPLAY_NAME"
    HEADLESS = "PLAYWRIGHT_HEADLESS"
    TIMEOUT = "PLAYWRIGHT_TIMEOUT"


def get_env(name: Env, default=None):
    return os.getenv(name.value, default)


def get_bool(name: Env, default: bool = True) -> bool:
    v = os.getenv(name.value)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")


def get_int(name: Env, default: int):
    v = os.getenv(name.value)
    try:
        return int(v)
    except Exception:
        return default
