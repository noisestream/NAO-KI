import json
from ws4py.websocket import WebSocket
from command_utils import set_single_nao

class CommandWebSocket(WebSocket):
    def opened(self):
        # Registriere beim Öffnen des Sockets als einziger NAO
        set_single_nao(self)

    def received_message(self, m):
        try:
            data = json.loads(m.data.decode('utf-8'))
            print("Nachricht vom NAO-Client:", data)
        except Exception as e:
            print("Fehler beim Verarbeiten der Nachricht:", e)

    def closed(self, code, reason=None):
        # Wenn der Client sich trennt, NAO-Referenz entfernen
        print("NAO-Client getrennt")
        set_single_nao(None)