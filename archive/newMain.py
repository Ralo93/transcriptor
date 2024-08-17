import threading
from newAudioCapture import AudioCapture
from WhisperClient import WhisperClient

def transcribe_audio(whisper_client, file_path):
    try:
        print(f"Transcribing {file_path}...")
        with open(file_path, "rb") as audio_file:
            transcription = whisper_client.transcribe(audio_file)
            print(f"Transcription of {file_path}: {transcription}")
    except Exception as e:
        print(f"Failed to transcribe {file_path}: {e}")

def main():
    audio_capture = AudioCapture()
    whisper_client = WhisperClient(api_key="")

    def capture_and_transcribe():
        for file_path in audio_capture.capture_audio():
            transcription_thread = threading.Thread(target=transcribe_audio, args=(whisper_client, file_path))
            transcription_thread.start()

    try:
        capture_and_transcribe()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        audio_capture.stop()

if __name__ == "__main__":
    main()
