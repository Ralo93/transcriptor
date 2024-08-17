import pyaudio
import webrtcvad
import os
import time
import io
from pydub import AudioSegment

class AudioCapture:
    def __init__(self, rate=16000, chunk_duration_ms=30, padding_duration_ms=300, save_dir=r"C:\Users\49176\Desktop\projects\easy GenAI API\audioFiles"):
        self.rate = rate
        self.chunk_duration_ms = chunk_duration_ms
        self.chunk_size = int(rate * chunk_duration_ms / 1000)
        self.padding_duration_ms = padding_duration_ms
        self.num_padding_chunks = int(padding_duration_ms / chunk_duration_ms)
        self.vad = webrtcvad.Vad(0)  # Least aggressive mode
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size)
        self.speech_timeout = 2  # Time in seconds to wait after the last speech detected
        self.save_dir = save_dir
        self.speech_trigger_count = 5  # Number of consecutive chunks with speech to start recording

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def is_speech(self, buffer):
        return self.vad.is_speech(buffer, self.rate)

    def capture_audio(self):
        triggered = False
        ring_buffer = []
        triggered_chunks = []
        speech_chunk_count = 0
        last_speech_time = None

        print("Listening for speech...")

        while True:
            chunk = self.stream.read(self.chunk_size)
            ring_buffer.append(chunk)
            ring_buffer = ring_buffer[-self.num_padding_chunks:]

            if self.is_speech(chunk):
                speech_chunk_count += 1
                if not triggered and speech_chunk_count > self.speech_trigger_count:
                    print("Consistent speech detected. Starting recording...")
                    triggered = True
                    triggered_chunks.extend(ring_buffer)
                    last_speech_time = time.time()
                if triggered:
                    triggered_chunks.append(chunk)
                    last_speech_time = time.time()
            else:
                if triggered:
                    speech_chunk_count = 0  # Reset count when no speech is detected
                    time_since_last_speech = time.time() - last_speech_time if last_speech_time else 0
                    if time_since_last_speech > self.speech_timeout:
                        print("No speech detected. Finalizing and saving audio segment...")
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
                        filepath = os.path.join(self.save_dir, f"debug_audio_{int(time.time())}.wav")
                        with open(filepath, "wb") as f:
                            f.write(wav_io.getvalue())

                        print(f"Audio file saved as {filepath}")

                        # Print the size of the BytesIO buffer to confirm data is written
                        print(f"Size of WAV file in memory: {wav_io.getbuffer().nbytes} bytes")

                        # Clear the buffer for the next recording segment
                        triggered_chunks = []
                        ring_buffer = []
                        speech_chunk_count = 0

                        yield filepath  # Return the path to the saved file
                else:
                    speech_chunk_count = 0  # Reset count when no speech is detected

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
