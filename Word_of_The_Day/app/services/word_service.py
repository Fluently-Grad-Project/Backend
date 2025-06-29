from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import DailyWord, FCMToken, WordOfTheDay
from app.Notification.fcm import WordOfTheDayPayload, send_word_notification


def insert_word_of_the_day_data(db: Session):
    words_data = [
        {
            "word": "facade",
            "parts_of_speech": "Noun",
            "description": "the front of a building",
            "example": "the facade of this bank is made of limestone",
        },
        {
            "word": "mitigate",
            "parts_of_speech": "Verb",
            "description": "to make something less harmful, unpleasant, or bad",
            "example": "Getting a lot of sleep and drinking plenty of fluids can mitigate the effects of the flu",
        },
        {
            "word": "Thrilling",
            "parts_of_speech": "Adjective",
            "description": "Very exciting or suspenseful; giving a rush of adrenaline.",
            "example": "Each scene was more thrilling than the last-I was on the edge of my seat.",
        },
        {
            "word": "sedentary",
            "parts_of_speech": "Adjective",
            "description": "involving little exercise or physical activity",
            "example": "My doctor says I should start playing sport because my lifestyle is too sedentary",
        },
        {
            "word": "incentive",
            "parts_of_speech": "Noun",
            "description": "something that encourages a person or organization to do something",
            "example": "Bonus payments provide an incentive to work harder",
        },
        {
            "word": "nauseous",
            "parts_of_speech": "Adjective",
            "description": "Causing a feeling of disgust or sickness.",
            "example": "The smell of rotten eggs was so nauseous that I had to leave the room",
        },
        {
            "word": "unspoiled",
            "parts_of_speech": "Adjective",
            "description": "(place)beautiful because it has not been changed or damaged by people.",
            "example": "With its unspoiled natural beauty, Vietnam is becoming a destination for more and more foreign visitors.",
        },
        {
            "word": "implacable",
            "parts_of_speech": "Adjective",
            "description": "(opinion or feeling) unable to be changed, satisfied, or stopped.",
            "example": "The dictator was implacable, refusing all attempts at negotiation",
        },
        {
            "word": "luscious",
            "parts_of_speech": "Adjective",
            "description": "describe something that has a delicious taste or smell; juicy.",
            "example": "Because the bread smelled luscious, Tom decided to go into the bakery.",
        },
        {
            "word": "Freak out",
            "parts_of_speech": "Phrasal verb (also used as a noun: 'a freak-out')",
            "description": "Get very scared or angry.",
            "example": "She freaked out when she saw the spider on her pillow.",
        },
        {
            "word": "Cameo",
            "parts_of_speech": "Noun",
            "description": "a brief appearance by a famous person in a film.",
            "example": "The director made a surprise cameo in the last scene.",
        },
        {
            "word": "Dope",
            "parts_of_speech": "Adjective",
            "description": "Awesome, excellent, or cool.",
            "example": "Your sneakers are so dope!.",
        },
        {
            "word": "Salty",
            "parts_of_speech": "Adjective",
            "description": "Being irritated, bitter, or overly upset (often about something unreasonable).",
            "example": "Why are you so salty? It's just a game!.",
        },
        {
            "word": "Hangry",
            "parts_of_speech": "Adjective",
            "description": "When you are so hungry that you are angry!.",
            "example": "Don't talk to me before breakfast—I get hangry!.",
        },
        {
            "word": "Lit",
            "parts_of_speech": "Adjective",
            "description": "Amazing, Exciting, or Fun",
            "example": "The concert was so lit! Everybody was dancing and having a great time.",
        },
        {
            "word": "Sus",
            "parts_of_speech": "Adjective",
            "description": "Suspicious",
            "example": "His behavior was kind of sus; he kept looking around like he was hiding something.",
        },
        {
            "word": "Bummer",
            "parts_of_speech": "Noun",
            "description": "A disappointment",
            "example": "That's such a bummer. I'm sorry that happened.",
        },
        {
            "word": "Screw up",
            "parts_of_speech": "Verb",
            "description": "To make a mistake",
            "example": "Sorry I screwed up and forgot our plans.",
        },
        {
            "word": "carillon",
            "parts_of_speech": "noun",
            "description": "a set of stationary bells hung in a tower",
            "example": "At noon on Tuesday, some church bells and carillons in the Netherlands didn't sound like they usually do.",
        },
        {
            "word": "Ace",
            "parts_of_speech": "Verb",
            "description": "To Perform Exceptionally Well",
            "example": "He aced the exam!.",
        },
        {
            "word": "eloquent",
            "parts_of_speech": "Adjective",
            "description": "An eloquent speaker or writer expresses ideas forcefully and fluently",
            "example": "She received high marks for her eloquent essay about gardening with her grandmother.",
        },
        {
            "word": "Resilient",
            "parts_of_speech": "Adjective",
            "description": "Able to recover quickly from difficulties",
            "example": "After losing her job, she showed how resilient she was by starting her own business.",
        },
        {
            "word": "Ambiguous",
            "parts_of_speech": "Adjective",
            "description": "Extremely large in size, quantity, or degree; gigantic.",
            "example": "An enormous elephant stood near the waterhole.",
        },
        {
            "word": "Sophisticated",
            "parts_of_speech": "Adjective",
            "description": "Having refined knowledge, culture, or taste; elegant.",
            "example": "His sophisticated manners impressed everyone at the dinner party.",
        },
        {
            "word": "Superb",
            "parts_of_speech": "Adjective",
            "description": "Of the highest quality; exceptionally good, excellent, or magnificent.",
            "example": "The chef prepared a superb five-course meal.",
        },
        {
            "word": "Awful",
            "parts_of_speech": "Adjective",
            "description": "Extremely bad/unpleasant.",
            "example": "The food was awful – I couldn't eat it.",
        },
        {
            "word": "Gratitude",
            "parts_of_speech": "Noun",
            "description": "A feeling of deep appreciation, thankfulness, or recognition for kindness, benefits, or favors received.",
            "example": "She expressed her gratitude with a heartfelt thank-you note.",
        },
        {
            "word": "Bed Rotting",
            "parts_of_speech": "Noun",
            "description": "when someone spends excessive time in bed doing passive activities (self-caring.), sometimes to the point of neglecting responsibilities.",
            "example": "I'm bed rotting all weekend—no plans, just snacks and Netflix.",
        },
        {
            "word": "Euphoria",
            "parts_of_speech": "Noun",
            "description": "A state of intense happiness, excitement, or confidence, often overwhelming or temporary.",
            "example": "That first sip of coffee gave me a little euphoria.",
        },
        {
            "word": "Compact",
            "parts_of_speech": "Adjective",
            "description": "Tiny, Closely packed or condensed; designed to save space.",
            "example": "She bought a compact car for city driving.",
        },
        {
            "word": "Gloomy",
            "parts_of_speech": "Adjective",
            "description": "Causing or reflecting sadness, hopelessness.",
            "example": "His gloomy mood ruined the party vibe.",
        },
        {
            "word": "Fascinating",
            "parts_of_speech": "Adjective",
            "description": "Extremely interesting or captivating; holding attention irresistibly.",
            "example": "She has a fascinating ability to remember every detail.",
        },
    ]

    for word_data in words_data:
        # Check if word already exists
        existing_word = db.query(WordOfTheDay).filter_by(word=word_data["word"]).first()
        if not existing_word:
            word_entry = WordOfTheDay(
                word=word_data["word"],
                parts_of_speech=word_data["parts_of_speech"],
                description=word_data["description"],
                example=word_data["example"],
            )
            db.add(word_entry)

    db.commit()


def schedule_word_of_the_day():
    scheduler = BackgroundScheduler()
    # Runs every day at midnight (00:00)
    scheduler.add_job(
        assign_todays_word,
        trigger=CronTrigger(hour=0, minute=0),
        name="Assign Word of the Day",
    )
    scheduler.start()


def assign_todays_word(db: Session):

    today = date.today()
    existing_word = db.query(DailyWord).filter(DailyWord.date == today).first()
    if existing_word:
        return
    random_word = db.query(WordOfTheDay).order_by(func.random()).first()

    # Assign it as today's word
    daily_word = DailyWord(date=today, word_id=random_word.id)
    db.add(daily_word)
    db.commit()


def send_daily_word_notification(db: Session):
    today = date.today()
    daily_word = db.query(DailyWord).filter(DailyWord.date == today).first()
    if not daily_word:
        raise HTTPException(status_code=404, detail="Today's word not found")
    fcm_tokens = db.query(FCMToken).filter(FCMToken.is_active.is_(True)).all()
    if not fcm_tokens:
        raise HTTPException(status_code=404, detail="No active FCM tokens found")
    for token in fcm_tokens:
        word_data = WordOfTheDayPayload(
            word=daily_word.word.word,
            parts_of_speech=daily_word.word.parts_of_speech,
            description=daily_word.word.description,
            example=daily_word.word.example,
        )
        send_word_notification(token=token.token, word_data=word_data)
