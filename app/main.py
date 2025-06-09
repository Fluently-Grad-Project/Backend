from fastapi import FastAPI
from app.api import user, auth, friend_routes, leaderboard_routes

app = FastAPI()

app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(friend_routes.router, prefix="/friends", tags=["Friends"])
app.include_router(leaderboard_routes.router, prefix="/leaderboard", tags=["Leaderboard"])
