import glob
import os

from DataStorage import DataStorage
from TextProcessor import TextProcessor
from WhisperClient import WhisperClient

def main():

    whisper_client = WhisperClient(api_key="")
    text_processor = TextProcessor()
    data_storage = DataStorage()

    for root, dirs, files in os.walk(r"C:\Users\49176\PycharmProjects\transcriptor\audio"):
        for file in files:

            transcription = whisper_client.transcribe_fromPath(os.path.join(root, file))
            print("Transcription:", transcription)
            print(os.path.join(root, file))
            text_processor.count_words(transcription)

    word_frequencies = text_processor.word_counter

    #TODO Add the actuan transcription to the database with timestamp
    data_storage.save_transcription(transcription, word_frequencies)

    frequencies = data_storage.get_word_frequencies()
    print(frequencies)

    def delete_all_recordings(directory):
        # Find all files in the specified directory
        files = glob.glob(f"{directory}/*")

        for file in files:
            try:
                # Delete each file
                os.remove(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Failed to delete {file}: {e}")

    delete_all_recordings(r"C:\Users\49176\PycharmProjects\transcriptor\audio")


if __name__ == "__main__":
    main()