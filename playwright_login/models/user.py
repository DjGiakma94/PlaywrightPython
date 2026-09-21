from dataclasses import dataclass


@dataclass
class User:
    username: str
    password: str
    display_name: str
