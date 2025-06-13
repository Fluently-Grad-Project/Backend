from fastapi import FastAPI
from app.api import user, auth, friend_routes, leaderboard_routes
from app.api.chat import router as chat_router
from app.core.websocket_manager import ConnectionManager
from fastapi.middleware.cors import CORSMiddleware
from app.api import matchmaking_routes
import logging

logging.basicConfig(
    filename="chat.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)
logger = logging.getLogger(__name__)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("security")


app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(friend_routes.router, prefix="/friends", tags=["Friends"])
app.include_router(
    leaderboard_routes.router, prefix="/leaderboard", tags=["Leaderboard"]
)
manager = ConnectionManager()
app.include_router(chat_router)
app.include_router(
    matchmaking_routes.router, prefix="/matchmaking", tags=["Matchmaking"]
)
