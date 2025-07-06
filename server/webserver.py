import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from websocket_server import CommandWebSocket
from openai_utils import generate_command_from_prompt
from command_utils import broadcast_command, get_single_nao

class Root(object):
    @cherrypy.expose
    def index(self):
        # Liefert das HTML-Interface zurück
        return open('index.html').read()

    @cherrypy.expose
    def ws(self):
        # Wichtig für WebSocket-Handshake
        cherrypy.request.ws_handler

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def send(self):
        # Prüfen, ob ein NAO verbunden ist
        if not get_single_nao():
            cherrypy.response.status = 503
            return {'status': 'error', 'message': 'Kein NAO verbunden'}

        data = cherrypy.request.json
        prompt = data.get('prompt', '')
        command = generate_command_from_prompt(prompt)
        broadcast_command(command)
        return {'status': 'ok', 'command': command}


def start_webserver(host="0.0.0.0", port=9000):
    cherrypy.config.update({
        "server.socket_host": host,
        "server.socket_port": port
    })
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
    config = {
        "/ws": {"tools.websocket.on": True,
                 "tools.websocket.handler_cls": CommandWebSocket}
    }
    cherrypy.tree.mount(Root(), "/", config)
    cherrypy.engine.start()


def stop_webserver():
    cherrypy.engine.exit()