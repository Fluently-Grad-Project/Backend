import os
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import whisper


class HateSpeechDetector:
    def __init__(
        self,
        tokenizer_name: str = "bert-base-uncased",
        state_dict_path: str = r"app\hate_detector_model\nlp_hate_detector_model (1).pth"
    ):
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_name)
        self.model = BertForSequenceClassification.from_pretrained(tokenizer_name, num_labels=3)
        self.model.load_state_dict(torch.load(state_dict_path, map_location=torch.device("cpu")))
        self.model.eval()
        self.labels = ["Friendly", "Offensive", "Hate"]

        whisper.audio.FFMPEG_PATH = r"C:\ffmpeg\ffmpeg.exe"
        self.whisper_model=whisper.load_model("base")

    def transcribe(self, audio_path: str) -> str:
        print(f"Checking file at: {audio_path}")
        print(f"Exists? {os.path.exists(audio_path)}")
        print("soooooooo ", self.whisper_model.transcribe(audio_path))
        return self.whisper_model.transcribe(audio_path)["text"]

    def predict(self, text: str) -> str:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
        return self.labels[pred]


hate_speech_detector = HateSpeechDetector()