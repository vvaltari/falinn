from fastapi import Depends
from src.db import get_db

async def get_user_collection(db = Depends(get_db)):
    return db.get_collection('users')