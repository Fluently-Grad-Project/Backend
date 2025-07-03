import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from fastapi.staticfiles import StaticFiles
logging.basicConfig(
    filename="chat.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)
logger = logging.getLogger(__name__)


app = FastAPI()


# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("security")


app.include_router(router)
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")