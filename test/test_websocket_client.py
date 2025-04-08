import websocket
import json
import time

def test_register_client(ws):
    ws.send(json.dumps({"client_id": "client_123"}))

def test_send_message(ws):
    ws.send(json.dumps({"message": "Hallo Server"}))

def test_invalid_json(ws):
    ws.send("{this is not: valid json")

def test_register_multiple(ws):
    for i in range(3):
        ws.send(json.dumps({"client_id": f"client_{i}"}))
        time.sleep(0.2)

def test_close_connection(ws):
    ws.close()

def on_open(ws):
    print("Verbindung geöffnet")

    # === Hier den gewünschten Testfall aufrufen ===
    test_register_client(ws)
    # test_send_message(ws)
    # test_invalid_json(ws)
    # test_register_multiple(ws)
    # test_close_connection(ws)

def on_message(ws, message):
    print("Nachricht vom Server:", message)

def on_error(ws, error):
    print("Fehler:", error)

def on_close(ws, close_status_code, close_msg):
    print("Verbindung geschlossen")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "ws://localhost:9000/",  # Passe die URL ggf. an
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()
