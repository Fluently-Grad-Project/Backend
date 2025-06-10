from fastapi import APIRouter, Depends
from datetime import date
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import DailyWord
from fastapi import HTTPException
router = APIRouter()

@router.get("/today")
def get_todays_word(db: Session = Depends(get_db)):
    today = date.today()
    daily_word = db.query(DailyWord).filter(DailyWord.date == today).first()
    
    if not daily_word:
        raise HTTPException(status_code=404, detail="Today's word not found")
    
    return {
        "word": daily_word.word.word,
        "parts_of_speech": daily_word.word.parts_of_speech,
        "description": daily_word.word.description,
        "example": daily_word.word.example,
    }