import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import threading
import json
import time
import pyaudio
import wave
import os
from dotenv import load_dotenv
from openai import OpenAI
from audio_utils import voice_input
from openai_utils import generate_command_from_prompt

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversation_history = [
    {
        "role": "system",
        "content": (
            "Du bist ein intelligenter NAO-Dialog-Manager. Es sind genau zwei NAOs verbunden: Gerda & Peter. "
            "Leite einen abwechselnden Dialog zwischen diesen beiden, SODASS SIE 3 BIS MAXIMAL 8 MAL ANTWORTEN, "
            "bevor der Dialog wieder an den Menschen zurückgegeben wird. "
            "In jeder Antwort gib den Schlüssel 'nextNao' an, der bestimmt, welcher NAO als Nächstes sprechen soll, "
            "und einen 'delay'-Wert in Sekunden, der angibt, wie lange gewartet werden soll, bevor der nächste Turn beginnt. "
            "Wenn der Dialog wieder an den Menschen übergeben werden soll, setze 'human_turn' auf true. "
            "Antworte stets als gültiges JSON-Objekt mit den Schlüsseln 'text', 'movement', 'nextNao', 'delay' und 'human_turn'. "
            "Beispiel: {\"text\": \"Ich winke dir zu!\", \"movement\": \"winken\", \"nextNao\": \"Peter\", \"delay\": 6, \"human_turn\": false}."
        )
    }
]

connected_clients = {}

class CommandWebSocket(WebSocket):
    def opened(self):
        print("Client verbunden:", self.peer_address)
    def received_message(self, m):
        try:
            data = json.loads(m.data.decode("utf-8"))
            if "client_id" in data:
                client_id = data["client_id"]
                connected_clients[client_id] = self
                print("Registrierter Client:", client_id)
            else:
                print("Nachricht vom Client:", data)
        except Exception as e:
            print("Fehler beim Verarbeiten der Nachricht:", e)
    def closed(self, code, reason=None):
        print("Client getrennt:", self.peer_address)
        for key, client in list(connected_clients.items()):
            if client == self:
                del connected_clients[key]
                print("Client {} entfernt".format(key))

class Root(object):
    @cherrypy.expose
    def index(self):
        return "WebSocket Server läuft!"
    @cherrypy.expose
    def ws(self):
        cherrypy.request.ws_handler

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
    # Angenommen 2,5 Wörter pro Sekunde, passe diesen Wert an, falls nötig
    estimated_duration = len(words) / 1.9  
    return max(min_delay, estimated_duration)

# --- Automatischer Konversationsmodus ---
def conversation_loop():
    print("Starte automatischen NAO-Konversationsmodus...")
    while True:
        command = generate_command_from_prompt("")
        if command.get("human_turn", False) or command.get("end_conversation", False):
            print("API signalisiert: Wechsel zurück zum Menschen.")
            break
        target_nao = command.get("nextNao")
        if target_nao and target_nao in connected_clients:
            broadcast_command(command, target_client=connected_clients[target_nao])
        else:
            if connected_clients:
                default_client = list(connected_clients.values())[0]
                broadcast_command(command, target_client=default_client)
            else:
                print("Keine NAO verbunden!")
                break
        text = command.get("text", "")
        api_delay = command.get("delay", 0)
        # Falls kein sinnvoller Delay von der API kommt, berechne dynamisch:
        if api_delay < 5:
            delay = calculate_delay(text, min_delay=5)
        else:
            delay = api_delay
        print(f"Warte {delay} Sekunden, bis der NAO seine Antwort beendet hat...")
        time.sleep(delay)
    print("Automatischer Dialog beendet. Zurück zum menschlichen Input.")

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
    cherrypy.config.update({
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 9000
    })
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
    config = {
        "/ws": {
            "tools.websocket.on": True,
            "tools.websocket.handler_cls": CommandWebSocket
        }
    }
    cherrypy.tree.mount(Root(), "/", config)
    cherrypy.engine.start()
    conversation_manager()
    cherrypy.engine.stop()
