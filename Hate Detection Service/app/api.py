import os
import uuid
import subprocess
from fastapi import APIRouter, UploadFile, File, HTTPException, Header
import httpx
from app.models.nlp_model import get_hate_detector

router = APIRouter()

@router.post("/analyze-audio")
async def analyze_audio(file: UploadFile = File(...), authorization: str | None = Header(None)):
    temp_dir = f"temp/{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)

    input_path = os.path.join(temp_dir, file.filename)
    output_path = os.path.join(temp_dir, "converted.wav")

    try:
        with open(input_path, "wb") as f:
            f.write(await file.read())

        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1", output_path
        ], check=True)

        detector = get_hate_detector()
        text = detector.transcribe(output_path)
        label = detector.predict(text)

        if label == "Offensive" or label=="Hate":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/notify-hate-speech",
                    json={"transcript": text, "label": label},
                    headers={"Authorization": authorization} if authorization else {}
                )
                response.raise_for_status()

        print(f"ℹ️: {text} ")
        print(f"ℹ️: {label} ")
        return {"transcript": text, "label": label}

    except subprocess.CalledProcessError:
        raise HTTPException(400, "FFmpeg audio conversion failed")
    except httpx.HTTPError as e:
        print(f"Error sending notification: {e}")
    finally:
        for file_path in [input_path, output_path]:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
