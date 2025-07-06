import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from websocket_server import CommandWebSocket
from openai_utils import generate_command_from_prompt
from command_utils import broadcast_command

class Root(object):
    @cherrypy.expose
    def index(self):
        # Kleines Webinterface für Text-Input und WebSocket-Status
        return '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>NAO Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; }
        #log { border: 1px solid #ccc; padding: 1rem; height: 300px; overflow-y: scroll; }
        #controls { margin-top: 1rem; }
        input[type=text] { width: 80%; padding: 0.5rem; }
        button { padding: 0.5rem 1rem; }
    </style>
</head>
<body>
    <h1>NAO Web-Interface</h1>
    <div id="status">Verbinde...</div>
    <div id="log"></div>

    <div id="controls">
        <input type="text" id="prompt" placeholder="Gib deinen Text ein..." />
        <button id="sendBtn">Senden</button>
    </div>

    <script>
        const logEl = document.getElementById('log');
        const statusEl = document.getElementById('status');
        const ws = new WebSocket(`ws://${location.host}/ws`);

        ws.onopen = () => {
            statusEl.textContent = 'WebSocket verbunden';
            // Client-ID registrieren
            ws.send(JSON.stringify({ client_id: 'web' }));
        };

        ws.onmessage = ({ data }) => {
            const msg = JSON.parse(data);
            const line = document.createElement('div');
            line.textContent = '> ' + JSON.stringify(msg);
            logEl.appendChild(line);
            logEl.scrollTop = logEl.scrollHeight;
        };

        ws.onclose = () => { statusEl.textContent = 'WebSocket getrennt'; };
        ws.onerror = err => { statusEl.textContent = 'Fehler: ' + err; };

        document.getElementById('sendBtn').onclick = () => {
            const prompt = document.getElementById('prompt').value;
            if (!prompt.trim()) return;
            fetch('/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            })
            .then(resp => resp.json())
            .then(data => {
                const line = document.createElement('div');
                line.textContent = '✔️ Gesendet: ' + prompt;
                logEl.appendChild(line);
                logEl.scrollTop = logEl.scrollHeight;
                document.getElementById('prompt').value = '';
            });
        };
    </script>
</body>
</html>
'''  # Ende HTML

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def send(self):
        # HTTP-Endpoint zum Senden eines Prompts an den NAO
        data = cherrypy.request.json
        prompt = data.get('prompt', '')
        command = generate_command_from_prompt(prompt)
        broadcast_command(command)
        return { 'status': 'ok', 'command': command }


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
