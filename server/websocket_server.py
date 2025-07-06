import json
from ws4py.websocket import WebSocket

from command_utils import set_single_nao

connected_clients = {}

class CommandWebSocket(WebSocket):
    def opened(self):
        set_single_nao(self)
        print("NAO-Client verbunden:", self.peer_address)

    #def received_message(self, m):
    #    try:
    #        data = json.loads(m.data.decode("utf-8"))
    #        if "client_id" in data:
    #            client_id = data["client_id"]
    #            connected_clients[client_id] = self
    #            print("Registrierter Client:", client_id)
    #        else:
    #            print("Nachricht vom Client:", data)
    #    except Exception as e:
    #        print("Fehler beim Verarbeiten der Nachricht:", e)

    def received_message(self, m):
        try:
            data = json.loads(m.data.decode("utf-8"))
            print("Nachricht vom NAO-Client:", data)
        except Exception as e:
            print("Fehler beim Verarbeiten der Nachricht:", e)

    #def closed(self, code, reason=None):
    #    print("Client getrennt:", self.peer_address)
    #    for key, client in list(connected_clients.items()):
    #        if client == self:
    #            del connected_clients[key]
    #            print("Client {} entfernt".format(key))


    def closed(self, code, reason=None):
        print("NAO-Client getrennt:", self.peer_address)
        from command_utils import single_nao_client
        if self == single_nao_client:
            set_single_nao(None)
            print("NAO-Client zurückgesetzt")