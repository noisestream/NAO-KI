import json
import cherrypy
from ws4py.websocket import WebSocket
from command_utils import set_single_nao, single_nao_client
 
class CommandWebSocket(WebSocket):
    def opened(self):
        # Neue WebSocket-Verbindung geöffnet
        print("WebSocket-Verbindung geöffnet:", self.peer_address)

    def received_message(self, m):
        try:
            data = json.loads(m.data.decode('utf-8'))
            ctype = data.get('client_type')

            # Registrierung des echten NAO-Clients
            if ctype == 'nao':
                set_single_nao(self)
                print("NAO-Client registriert:", data.get('client_id'))

            # Web-UI-Client, nur Logging
            elif ctype == 'web':
                print("Web-UI verbunden")

            # Alle anderen Nachrichten (z.B. Statusmeldungen, Antworten)
            else:
                print("Nachricht vom NAO-Client:", data)

        except Exception as e:
            print("Fehler beim Verarbeiten der Nachricht:", e)

    def closed(self, code, reason=None):
        # Entferne NAO-Referenz, wenn sich der NAO trennt
        if self == single_nao_client:
            set_single_nao(None)
            print("NAO-Client zurückgesetzt")
        print("WebSocket-Verbindung geschlossen:", self.peer_address)


def start_websocket_plugin():
    # Wird in webserver.py aufgerufen, muss hier nicht erneut definiert werden
    pass
