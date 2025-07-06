# server/dialog_loop.py
import time
from openai_utils import generate_command_from_prompt
from command_utils import broadcast_command, calculate_delay, get_single_nao

def conversation_loop(max_turns=3):
    print("Starte automatischen NAO-Konversationsmodus...")
    turns = 0

    while True:
        if turns >= max_turns:
            print("🔚 Maximalanzahl Runden erreicht, zurück zum Menschen.")
            break

        # Leere Aufforderung -> Modell fährt fort
        command = generate_command_from_prompt("")

        if command.get("end_conversation", False):
            print("🛑 Modell signalisiert: Konversation beenden.")
            break
        if command.get("human_turn", False):
            print("🛑 Modell signalisiert: Mensch ist wieder dran.")
            break

        # Sende an NAO
        broadcast_command(command)

        text = command.get("text", "")
        api_delay = command.get("delay", 0)
        delay = api_delay if api_delay >= 5 else calculate_delay(text, min_delay=5)
        print(f"Warte {delay:.1f}s bis zur nächsten Antwort...")
        time.sleep(delay)

        turns += 1

    print("🟢 Automatischer Dialogmodus beendet.")
