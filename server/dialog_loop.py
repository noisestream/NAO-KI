import time
from openai_utils import generate_command_from_prompt
from command_utils import broadcast_command, calculate_delay, get_single_nao
# from websocket_server import connected_clients

#def conversation_loop():
#    print("Starte automatischen NAO-Konversationsmodus...")
#    while True:
#        command = generate_command_from_prompt("")
#        if command.get("human_turn", False) or command.get("end_conversation", False):
#            print("API signalisiert: Wechsel zurück zum Menschen.")
#            break

#        target_nao = command.get("nextNao")
#        if target_nao and target_nao in connected_clients:
#            broadcast_command(command, target_client=connected_clients[target_nao])
#        else:
#            if connected_clients:
#                default_client = list(connected_clients.values())[0]
#                broadcast_command(command, target_client=default_client)
#            else:
#                print("Keine NAO verbunden!")
#                break

#        text = command.get("text", "")
#        api_delay = command.get("delay", 0)
#        delay = api_delay if api_delay >= 5 else calculate_delay(text, min_delay=5)
#        print(f"Warte {delay} Sekunden, bis der NAO seine Antwort beendet hat...")
#        time.sleep(delay)

#    print("Automatischer Dialog beendet. Zurück zum menschlichen Input.")

import time
from openai_utils import generate_command_from_prompt
from command_utils import broadcast_command, calculate_delay, get_single_nao

def conversation_loop():
    print("Starte automatischen NAO-Konversationsmodus...")
    while True:
        if not get_single_nao():
            print("❌ Kein NAO verbunden.")
            break

        command = generate_command_from_prompt("")
        if command.get("human_turn", False) or command.get("end_conversation", False):
            print("API signalisiert: Zurück zum Menschen.")
            break

        broadcast_command(command)

        text = command.get("text", "")
        api_delay = command.get("delay", 0)
        delay = api_delay if api_delay >= 5 else calculate_delay(text, min_delay=5)
        print(f"Warte {delay:.1f}s bis zur nächsten Antwort...")
        time.sleep(delay)

    print("🟢 Dialogmodus beendet.")
