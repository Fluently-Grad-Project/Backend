import os
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import whisper

class HateSpeechDetector:
    def __init__(
        self,
        tokenizer_name: str = "bert-base-uncased",
        state_dict_path: str = r"app\hate_detector_model\nlp_hate_detector_model (1).pth",
        whisper_model_name: str = "base",
        ffmpeg_path: str = r"C:\ffmpeg\ffmpeg.exe",
    ):
        self.tokenizer_name = tokenizer_name
        self.state_dict_path = state_dict_path
        self.whisper_model_name = whisper_model_name
        self.ffmpeg_path = ffmpeg_path

        self.tokenizer = None
        self.model = None
        self.labels = ["Friendly", "Offensive", "Hate"]
        self.whisper_model = None
        self.initialized = False

    def _initialize(self):
        if self.initialized:
            return

        whisper.audio.FFMPEG_PATH = self.ffmpeg_path
        self.tokenizer = BertTokenizer.from_pretrained(self.tokenizer_name)
        self.model = BertForSequenceClassification.from_pretrained(self.tokenizer_name, num_labels=3)
        self.model.load_state_dict(torch.load(self.state_dict_path, map_location=torch.device("cpu")))
        self.model.eval()
        self.whisper_model = whisper.load_model(self.whisper_model_name)

        self.initialized = True

    def transcribe(self, audio_path: str) -> str:
        self._initialize()
        print(f"Checking file at: {audio_path}")
        print(f"Exists? {os.path.exists(audio_path)}")
        return self.whisper_model.transcribe(audio_path)["text"]

    def predict(self, text: str) -> str:
        self._initialize()
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
        return self.labels[pred]

hate_speech_detector = HateSpeechDetector()