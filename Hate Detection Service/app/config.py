from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ffmpeg_path: str = "ffmpeg"
    whisper_model_size: str = "base"

    class Config:
        env_file = ".env"

settings = Settings()
