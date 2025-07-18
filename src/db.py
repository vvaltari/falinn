import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

def get_db():
    DB_URI = os.getenv('DB_URI')
    DB_NAME = os.getenv('DB_NAME')
    client = AsyncIOMotorClient(DB_URI)
    return client[DB_NAME]