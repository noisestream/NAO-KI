import json
import time
from websocket_server import connected_clients

_message_counter = 0

def broadcast_command(command, target_client=None):
    global _message_counter
    _message_counter += 1
    command["msg_id"] = _message_counter  # Neue Nachrichtennummer hinzufügen

    message = json.dumps(command)
    if target_client:
        try:
            target_client.send(message)
            print(f"[{_message_counter}] Befehl an {command.get('nextNao')}: {message}")
        except Exception as e:
            print(f"[{_message_counter}] Fehler beim Senden an {command.get('nextNao')}: {e}")
    else:
        print(f"[{_message_counter}] Sende an alle: {message}")
        for client in connected_clients.values():
            try:
                client.send(message)
            except Exception as e:
                print(f"[{_message_counter}] Fehler beim Senden an einen Client: {e}")

def calculate_delay(text, min_delay=5):
    words = text.split()
    estimated_duration = len(words) / 1.9  # geschätzt 1.9 w/s
    return max(min_delay, estimated_duration)
