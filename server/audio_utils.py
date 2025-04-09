import threading
import pyaudio
import wave
import os

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
OUTPUT_FILENAME = "recording.wav"

def transcribe_audio(filename):
    print("Sende Audiodatei an Whisper API...")
    with open(filename, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

def voice_input():
    filename = record_audio()
    text = transcribe_audio(filename)
    print("Transkription:", text)
    return text

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    input("Drücke Enter, um die Aufnahme zu starten...")
    print("Aufnahme läuft... Drücke Enter, um zu stoppen.")
    recording = [True]
    def wait_for_stop():
        input()
        recording[0] = False
    stop_thread = threading.Thread(target=wait_for_stop)
    stop_thread.start()
    while recording[0]:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        except Exception as e:
            print("Fehler beim Aufnehmen:", e)
            break
    print("Aufnahme beendet.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return OUTPUT_FILENAME
