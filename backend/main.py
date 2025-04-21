import logging
logging.info("Loading backend/main.py")

from fastapi import FastAPI
from app.routes import auth

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

app.include_router(auth.router)
