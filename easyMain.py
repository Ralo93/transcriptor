import pyaudio
import webrtcvad
import wave
import collections
import time
import os

from DataStorage import DataStorage

class AudioCapture:
    def __init__(self, aggressiveness=3, pause_time=2, output_dir=r"C:\Users\49176\PycharmProjects\transcriptor\audio"):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.pause_time = pause_time
        self.chunk_duration_ms = 30  # Duration of a single chunk in ms
        self.sample_rate = 16000  # WebRTC VAD works with 16kHz audio
        self.chunk_size = int(self.sample_rate * self.chunk_duration_ms / 1000)
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=self.sample_rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)
        self.speech_buffer = collections.deque(maxlen=int(1000 / self.chunk_duration_ms))
        self.audio_buffer = []
        self.last_speech_time = time.time()
        self.is_speaking = False
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.file_index = 0


    def is_speech(self, data):
        return self.vad.is_speech(data, self.sample_rate)

    def save_audio(self, frames):

        timestamp = time.strftime("%Y%m%d_%H%M%S")

        filename = os.path.join(self.output_dir, f"speech_{timestamp}.wav")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
        print(f"Saved {filename}")
        self.file_index += 1

    def start(self):
        try:
            print("Listening...")
            while True:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.speech_buffer.append((self.is_speech(data), time.time()))
                self.audio_buffer.append(data)

                if any(speech for speech, _ in self.speech_buffer):
                    if not self.is_speaking:
                        print("Speaking!")
                        self.is_speaking = True
                    self.last_speech_time = time.time()
                else:
                    if self.is_speaking and time.time() - self.last_speech_time > self.pause_time:
                        print("Stopped speaking...")
                        self.save_audio(self.audio_buffer)
                        self.audio_buffer = []  # Reset buffer after saving
                        self.is_speaking = False

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

if __name__ == "__main__":
    capture = AudioCapture()
    capture.start()
