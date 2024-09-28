from datetime import datetime
from config import Config

class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {"usage_count": 0, "last_used": datetime.now().date()}

    def can_use_service(self, user_id):
        if user_id not in self.users:
            self.add_user(user_id)
        
        user_data = self.users[user_id]
        if user_data["last_used"] < datetime.now().date():
            user_data["usage_count"] = 0
            user_data["last_used"] = datetime.now().date()
        
        return user_data["usage_count"] < Config.DAILY_LIMIT

    def increment_usage(self, user_id):
        if user_id in self.users:
            self.users[user_id]["usage_count"] += 1
            self.users[user_id]["last_used"] = datetime.now().date()