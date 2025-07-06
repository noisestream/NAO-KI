import websocket
import threading
import time
import json

CLIENT_ID = "SimNAO"

def on_message(ws, message):
    try:
        data = json.loads(message)
        print("📥 Befehl vom Server empfangen:", data)
        # Hier könntest du z. B. Bewegung simulieren
    except Exception as e:
        print("❌ Fehler beim Verarbeiten der Nachricht:", e)

def on_open(ws):
    print("✅ Verbindung zum Server geöffnet.")
    # Registriere dich mit client_id
    register_msg = json.dumps({"client_id": CLIENT_ID})
    ws.send(register_msg)

def on_close(ws, close_status_code, close_msg):
    print("❌ Verbindung geschlossen:", close_status_code, close_msg)

def on_error(ws, error):
    print("❌ Fehler:", error)

def start_dummy_nao():
    ws = websocket.WebSocketApp(
        "ws://localhost:9000/ws",
        on_open=on_open,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error
    )

    # Starte im Thread, um reconnect zu ermöglichen
    thread = threading.Thread(target=ws.run_forever)
    thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Beenden...")

if __name__ == "__main__":
    start_dummy_nao()
