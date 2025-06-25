# python -m app.main
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import word
from app.database.connection import get_db
from app.Notification import fcm
from app.services.word_service import (
    assign_todays_word,
    insert_word_of_the_day_data,
    send_daily_word_notification,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="add any string...")
app.include_router(fcm.router, prefix="/fcm", tags=["FCM Notifications"])
app.include_router(word.router, prefix="/word-of-the-day", tags=["Word of the Day"])
scheduler = BackgroundScheduler()


def initialize_word_of_the_day():
    db = next(get_db())
    try:
        insert_word_of_the_day_data(db)
        print("Word of the day data inserted successfully")
    except Exception as e:
        print(f"Error inserting word of the day data: {e}")
    finally:
        db.close()


def send_daily_notification_job():
    db = next(get_db())
    try:

        send_daily_word_notification(db)
        print(f"Notification sent at {datetime.now()}")
    except Exception as e:
        print(f"Error sending notification: {e}")
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    db = next(get_db())
    initialize_word_of_the_day()
    assign_todays_word(db)

    scheduler.add_job(
        send_daily_notification_job,
        CronTrigger(hour=20, minute=0),  # 8 PM (20:00)
        name="daily_word_notification",
    )
    scheduler.start()
    print("Scheduler started - Notifications will run daily at 8 PM")


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    print("Scheduler shut down")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  
