"""
Represents a user in the system.
"""
class User:
    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return f"User(user_id='{self.user_id}')"
