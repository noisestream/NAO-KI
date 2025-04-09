import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from websocket_server import CommandWebSocket

class Root(object):
    @cherrypy.expose
    def index(self):
        return "WebSocket Server läuft!"
    
    @cherrypy.expose
    def ws(self):
        cherrypy.request.ws_handler  # wichtig für ws4py
        

def start_webserver(host="0.0.0.0", port=9000):
    cherrypy.config.update({
        "server.socket_host": host,
        "server.socket_port": port
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

def stop_webserver():
    cherrypy.engine.exit()
