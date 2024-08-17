import pyaudio
import webrtcvad
import io
from pydub import AudioSegment
import time

class AudioCapture:
    def __init__(self, rate=16000, chunk_duration_ms=30, padding_duration_ms=300):
        self.rate = rate
        self.chunk_duration_ms = chunk_duration_ms
        self.chunk_size = int(rate * chunk_duration_ms / 1000)
        self.padding_duration_ms = padding_duration_ms
        self.num_padding_chunks = int(padding_duration_ms / chunk_duration_ms)
        self.vad = webrtcvad.Vad(0)  # Use a less aggressive VAD level (0 is least, 3 is most)
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)
        self.speech_timeout = 1  # Time in seconds to wait after the last speech detected

    def is_speech(self, buffer):
        return self.vad.is_speech(buffer, self.rate)

    def capture_audio(self):
        triggered = False
        ring_buffer = []
        triggered_chunks = []
        last_speech_time = time.time()

        print("Listening for speech...")

        while True:
            chunk = self.stream.read(self.chunk_size)
            ring_buffer.append(chunk)
            ring_buffer = ring_buffer[-self.num_padding_chunks:]

            if self.is_speech(chunk):
                if not triggered:
                    triggered = True
                    triggered_chunks.extend(ring_buffer)
                    last_speech_time = time.time()
                triggered_chunks.append(chunk)
                last_speech_time = time.time()
            else:
                if triggered and (time.time() - last_speech_time) > self.speech_timeout:
                    # Speech has ended and timeout reached, finalize the segment
                    triggered = False

                    # Combine audio chunks and convert to AudioSegment
                    audio_data = b''.join(triggered_chunks)
                    audio_segment = AudioSegment(
                        data=audio_data,
                        sample_width=2,  # 16-bit PCM
                        frame_rate=self.rate,
                        channels=1  # Mono
                    )

                    # Export AudioSegment to WAV in-memory
                    wav_io = io.BytesIO()
                    audio_segment.export(wav_io, format="wav")
                    wav_io.seek(0)  # Reset the stream position to the beginning

                    # Save the WAV file to disk for debugging
                    with open(r"C:\Users\49176\Desktop\projects\easy GenAI API\debug_audio.wav", "wb") as f:
                        f.write(wav_io.getvalue())

                    print("Audio file saved as debug_audio.wav for inspection.")

                    # Print the size of the BytesIO buffer to confirm data is written
                    print(f"Size of WAV file in memory: {wav_io.getbuffer().nbytes} bytes")

                    # Clear the buffer for the next recording segment
                    triggered_chunks = []
                    ring_buffer = []


                    yield wav_io



    def stop(self):
        print("Stopping audio capture...")
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
