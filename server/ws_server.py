import time
import pyaudio
import wave
from audio_utils import voice_input
from openai_utils import generate_command_from_prompt
from webserver import start_webserver
from command_utils import broadcast_command, calculate_delay
from dialog_loop import conversation_loop

# --- Gesprächsmanager (Wechsel zwischen menschlicher Eingabe und automatischem Modus) ---
def conversation_manager():
    while True:
        mode = input("Wähle Eingabemodus ('t' für Text, 'v' für Voice, 'exit' zum Beenden): ").strip().lower()
        if mode == "exit":
            break
        if mode == "v":
            prompt = voice_input()
        elif mode == "t":
            prompt = input("Gib deine Texteingabe ein: ")
        else:
            print("Ungültige Auswahl. Bitte 't' oder 'v' eingeben.")
            continue
        command = generate_command_from_prompt(prompt)
        target_nao = command.get("nextNao")
        if target_nao and target_nao in connected_clients:
            broadcast_command(command, target_client=connected_clients[target_nao])
        else:
            broadcast_command(command)
        conversation_loop()

# --- Main Block: Webserver im Hintergrund ---
if __name__ == '__main__':
    start_webserver()
    conversation_manager()
    cherrypy.engine.stop()
