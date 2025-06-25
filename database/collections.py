from conn import db

user_collection = db.get_collection('users')
secret_collection = db.get_collection('secrets')