from sqlite3 import Connection
from typing import Optional

class User:
    def __init__(self, user_id: int, username: Optional[str] = None):
        self.user_id = user_id
        self.username = username

class SentImage:
    def __init__(self, user_id: int, file_id: str, date: int):
        self.user_id = user_id
        self.file_id = file_id
        self.date = date