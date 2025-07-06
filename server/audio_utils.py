import os
import threading
import pyaudio
import wave
import json
import sys
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv

load_dotenv()

# Audio-Konfiguration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
OUTPUT_FILENAME = "recording.wav"

# Pfad zum Vosk-Sprachmodell
MODEL_PATH = os.path.expanduser("~/nao-ki/models/vosk-model-de-0.21")
vosk_model = Model(MODEL_PATH)

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    frames = []

    user_input = input("🎤 Drücke Enter, um die Aufnahme zu starten... (oder 'exit' zum Beenden) ")

    if user_input.strip().lower() == 'exit':
        print("Programm wird beendet.")
        sys.exit(0)

    print("🟢 Aufnahme läuft... Drücke Enter, um zu stoppen.")

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
            print("❌ Fehler beim Aufnehmen:", e)
            break

    print("⏹️ Aufnahme beendet.")
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

def transcribe_audio(filename):
    print("🧠 Starte lokale Spracherkennung mit Vosk...")

    wf = wave.open(filename, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError("WAV-Datei muss 16kHz Mono PCM sein")

    recognizer = KaldiRecognizer(vosk_model, wf.getframerate())
    recognizer.SetWords(True)

    result_text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_text += json.loads(result).get("text", "") + " "

    final_result = json.loads(recognizer.FinalResult())
    result_text += final_result.get("text", "")

    return result_text.strip()

def voice_input():
    filename = record_audio()
    text = transcribe_audio(filename)
    print("📝 Transkription:", text)
    return text
