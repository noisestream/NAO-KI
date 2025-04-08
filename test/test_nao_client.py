import sys
import json
import random
from ws4py.client.threadedclient import WebSocketClient

CLIENT_ID = f"NAO-Test-{random.randint(1, 1000)}"

class NAOWebSocketClient(WebSocketClient):
    def opened(self):
        print("Verbindung geöffnet:", self.peer_address)
        # Registrierungsnachricht an den Server senden
        self.send(json.dumps({"client_id": CLIENT_ID}))

    def closed(self, code, reason=None):
        print("Verbindung geschlossen: Code =", code, "Reason =", reason)

    def received_message(self, m):
        print("Nachricht erhalten:", m.data)
        command = json.loads(m.data.decode("utf-8"))
        if "text" in command:
            print("Text erhalten:", command["text"])
        if "movement" in command:
            print("Bewegung erhalten:", command["movement"])

    def execute_text(self, text):
        if not isinstance(text, str):
            text = text.decode("utf-8", "ignore")
        print("Sprachausgabe ausführen:", text)

    def execute_motion(self, motion_command):
        print("Bewegung ausführen:", motion_command)

if __name__ == '__main__':
    # Setze hier die WebSocket-URL deines Servers; ersetze <Laptop-IP> durch die tatsächliche IP (z.B. "192.168.1.50")
    ws_url = 'ws://0.0.0.0:9000/ws'

    try:
        ws = NAOWebSocketClient(ws_url, protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
