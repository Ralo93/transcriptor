import requests
from openai import OpenAI


class WhisperClient:
    def __init__(self, api_key, api_url="https://api.whisper.cloud/transcribe"):
        self.api_key = api_key
        self.api_url = api_url
        self.client = OpenAI(api_key=api_key)

    def transcribe(self, audio_data):
        print(audio_data)
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_data
        )
        return transcription.text

    def transcribe_fromPath(self, file_path):
        # Test with a known good WAV file
        with open(file_path, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text