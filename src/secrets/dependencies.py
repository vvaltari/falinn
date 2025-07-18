from fastapi import Depends
from src.db import get_db

async def get_secret_collection(db = Depends(get_db)):
    return db.get_collection('secrets')