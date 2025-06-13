from cachetools import TTLCache, cached
from datetime import datetime
import sqlalchemy
import pandas as pd
from typing import List, Tuple
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.user_schemas import MatchedUserResponse
from app.database.models import UserData, MatchMaking, UserManager
from sqlalchemy.orm import Session
from fastapi import HTTPException
# Cache similar users for 15 minutes (900 seconds)
similar_users_cache = TTLCache(maxsize=128, ttl=300)
user_details_cache = TTLCache(maxsize=256, ttl=300)
@cached(similar_users_cache)
def get_similar_users(user_id: int, n_recommendations: int = 5) -> List[Tuple[int, float]]:
    """Get similar active non-friend users with their similarity scores"""
    print(f"Computing similar users for {user_id}")  # Debug to see cache hits
    
    engine = sqlalchemy.create_engine("postgresql://postgres:asdqwe123@localhost/fluently")
    
    try:
        query = f"""
        WITH user_friends AS (
            SELECT friend_id FROM friendship WHERE user_id = {user_id}
            UNION
            SELECT user_id FROM friendship WHERE friend_id = {user_id}
        )
        SELECT 
            ud.id as user_id, 
            mm.interests, 
            mm.practice_frequency, 
            mm.proficiency_level, 
            ud.birth_date, 
            ud.gender,
            ud.first_name,
            ud.last_name
        FROM matchmaking mm
        JOIN user_data ud ON mm.user_id = ud.id
        WHERE 
            ud.is_active = TRUE
            AND ud.id != {user_id}
            AND ud.id NOT IN (SELECT friend_id FROM user_friends)
        """
        
        users_df = pd.read_sql(query, engine)
        
        if users_df.empty:
            return []

        # Feature engineering
        interests = users_df['interests'].apply(lambda x: x if isinstance(x, list) else [])
        mlb = MultiLabelBinarizer()
        interests_encoded = pd.DataFrame(
            mlb.fit_transform(interests),
            columns=[f"int_{x}" for x in mlb.classes_],
            index=users_df.index
        )
        
        practice_encoded = pd.get_dummies(
            users_df['practice_frequency'].fillna('missing'),
            prefix='practice'
        )
        
        proficiency_encoded = pd.get_dummies(
            users_df['proficiency_level'].fillna('missing'),
            prefix='proficiency'
        )
        
        current_date = datetime.now()
        dob = pd.to_datetime(users_df['birth_date'])
        users_df['Age'] = (current_date.year - dob.dt.year) - (
            (current_date.month < dob.dt.month) | 
            ((current_date.month == dob.dt.month) & (current_date.day < dob.dt.day))
        )
        scaler = MinMaxScaler()
        age_scaled = pd.DataFrame(
            scaler.fit_transform(users_df[['Age']]),
            columns=['age_scaled'],
            index=users_df.index
        )
        
        gender_encoded = pd.get_dummies(
            users_df['gender'].fillna('missing'),
            prefix='gender'
        )
        
        final_features = pd.concat([
            interests_encoded,
            practice_encoded,
            proficiency_encoded,
            age_scaled
        ], axis=1).fillna(0)
        
        similarity_matrix = cosine_similarity(final_features)
        
        similar_indices = similarity_matrix[0].argsort()[::-1][:n_recommendations]
        return [
            (users_df.iloc[idx]['user_id'], similarity_matrix[0][idx])
            for idx in similar_indices
        ]
        
    except Exception as e:
        print(f"Error in get_similar_users: {e}")
        return []
    finally:
        engine.dispose()

# Cache user details for 1 hour
@cached(user_details_cache)
def get_user_details(user_id: int, db: Session) -> dict:
    """Cache individual user details"""
    user = db.query(
        UserData,
        MatchMaking.interests,
        UserManager.rating,
        UserData.birth_date,
        UserData.gender
    )\
        .join(MatchMaking, UserData.id == MatchMaking.user_id)\
        .outerjoin(UserManager, UserData.id == UserManager.user_data_id)\
        .filter(UserData.id == user_id)\
        .first()
    
    if not user:
        return None
        
    user_data, interests, rating, birth_date, gender = user
    current_date = datetime.now()
    age = current_date.year - birth_date.year - (
        (current_date.month, current_date.day) < 
        (birth_date.month, birth_date.day)
    )
    
    return {
        'user_id': user_data.id,
        'username': f"{user_data.first_name} {user_data.last_name}",
        'interests': interests if interests else [],
        'rating': float(rating) if rating is not None else None,
        'age': age,
        'gender': gender
    }

def get_similar_users_details(user_id: int, db: Session, n_recommendations: int = 5) -> List[MatchedUserResponse]:
    """Get detailed information about similar users"""
    try:
        user_id = int(user_id) if hasattr(user_id, 'item') else user_id
        
        similar_users = get_similar_users(user_id=user_id, n_recommendations=n_recommendations)
        
        if not similar_users:
            return []
        
        matched_users = []
        for user_id, score in similar_users:
            user_id = int(user_id) if hasattr(user_id, 'item') else user_id
            user_details = get_user_details(user_id, db)
            
            if user_details:
                matched_users.append(MatchedUserResponse(
                    user_id=user_details['user_id'],
                    username=user_details['username'],
                    interests=user_details['interests'],
                    rating=user_details['rating'],
                    age=user_details['age'],
                    gender=user_details['gender'],
                    similarity_score=float(score)
                ))
        
        return matched_users
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))