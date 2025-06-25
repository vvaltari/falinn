from fastapi import FastAPI
from routers.auth import auth_router
from routers.users import users_router
from routers.secrets import secrets_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(secrets_router)
