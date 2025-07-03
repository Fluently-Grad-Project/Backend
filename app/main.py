import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.language_middleware import LanguageMiddleware
from app.services.report_service import ReportService
from app.api import auth, friend_routes, leaderboard_routes, matchmaking_routes, user,reports,activity
from app.api.chat import router as chat_router
from app.core.websocket_manager import ConnectionManager
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database.connection import get_db
logging.basicConfig(
    filename="chat.log", level=logging.INFO, format="%(asctime)s - %(message)s"
)
logger = logging.getLogger(__name__)


app = FastAPI()


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


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
app.include_router(
    reports.router, prefix="/reports", tags=["Reports"]
)
app.include_router(
    activity.router, prefix="/activity", tags=["Activity"])
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.add_middleware(LanguageMiddleware)

from apscheduler.schedulers.background import BackgroundScheduler
db = next(get_db())
@app.on_event("startup")
def init_scheduler():
    scheduler = BackgroundScheduler()
    
    def check_job():
        
        try:
            print("Checking suspended users...")
            ReportService(db).check_expired_suspensions()
        except Exception as e:
            print(f"Error checking suspensions: {e}")
        finally:
            db.close()
    
  
    scheduler.add_job(check_job, 'interval', hours=1)
    scheduler.add_job(
    lambda: activity.reset_inactive_streaks(db),  
    CronTrigger(hour=18, minute=19),
    name='reset_inactive_streaks'
)
    scheduler.start()
    print("Streak reset at 00:05 AM")

    