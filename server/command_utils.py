import json
import time
from websocket_server import connected_clients

def broadcast_command(command, target_client=None):
    message = json.dumps(command)
    if target_client:
        try:
            target_client.send(message)
            print(f"Befehl an {command.get('nextNao')} gesendet: {message}")
        except Exception as e:
            print(f"Fehler beim Senden an {command.get('nextNao')}: {e}")
    else:
        print("Kein spezifischer NAO angegeben, sende an alle:", message)
        for client in connected_clients.values():
            try:
                client.send(message)
            except Exception as e:
                print("Fehler beim Senden an einen Client:", e)

def calculate_delay(text, min_delay=5):
    words = text.split()
    estimated_duration = len(words) / 1.9  # geschätzt 1.9 w/s
    return max(min_delay, estimated_duration)
