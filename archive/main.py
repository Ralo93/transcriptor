import time
from threading import Thread

from AudioCapture import AudioCapture
from DataStorage import DataStorage
from TextProcessor import TextProcessor
from UI import run_web_app
from WhisperClient import WhisperClient


def main():
    audio_capture = AudioCapture()
    whisper_client = WhisperClient(api_key="")
    text_processor = TextProcessor()
    storage = DataStorage()

    # Start the web app in a separate thread
    web_app_thread = Thread(target=run_web_app, args=(storage,))
    web_app_thread.start()

    try:
        for audio_data in audio_capture.capture_audio():
            print("Transcribing...")

            transcription = whisper_client.transcribe(audio_data)
            print("Transcription:", transcription)

            word_frequencies = text_processor.count_words(transcription)
            print("Word Frequencies:", word_frequencies)

            storage.save_transcription(transcription, word_frequencies)

            time.sleep(1)  # Avoid hammering the API too quickly in a real-time scenario

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        audio_capture.stop()
        #storage.close()

if __name__ == "__main__":
    main()
