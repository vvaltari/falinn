from src.dependencies import get_db

db = get_db()

user_collection = db.get_collection('users')