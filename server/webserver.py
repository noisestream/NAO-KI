import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from websocket_server import CommandWebSocket
from audio_utils import voice_input
from openai_utils import generate_command_from_prompt
from command_utils import broadcast_command, get_single_nao

class Root(object):
    @cherrypy.expose
    def index(self):
        # HTML-Interface für NAO-Konversation
        html = """
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>NAO Konversation</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    #controls { margin-bottom: 1rem; }
    button, select { padding: 0.5rem; margin-right: 0.5rem; }
    #log { border: 1px solid #ccc; padding: 1rem; height: 400px; overflow-y: auto; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>NAO Konversations-Interface</h1>
  <div id="controls">
    <label for="mode">Eingabemodus:</label>
    <select id="mode">
      <option value="t">Text</option>
      <option value="v">Voice (Server)</option>
    </select>
    <button id="start">Modus setzen</button>
  </div>

  <div id="inputArea">
    <input type="text" id="userInput" placeholder="Deine Nachricht..." style="width: 60%; padding:0.5rem;" />
    <button id="sendBtn">Senden</button>
    <button id="voiceBtn" style="display:none;">Aufnahme Starten</button>
  </div>

  <div id="log"></div>

  <script>
    let mode = 't';
    function log(msg) {
      const logEl = document.getElementById('log');
      logEl.textContent += msg + '\n';
      logEl.scrollTop = logEl.scrollHeight;
    }
    document.getElementById('start').onclick = () => {
      mode = document.getElementById('mode').value;
      document.getElementById('userInput').style.display = mode==='t' ? 'inline-block' : 'none';
      document.getElementById('sendBtn').style.display  = mode==='t' ? 'inline-block' : 'none';
      document.getElementById('voiceBtn').style.display = mode==='v' ? 'inline-block' : 'none';
      log('Modus gesetzt auf ' + (mode==='t' ? 'Text' : 'Voice'));
    };

    document.getElementById('sendBtn').onclick = () => {
      const prompt = document.getElementById('userInput').value;
      if (!prompt.trim()) return;
      fetch('/prompt', {
        method: 'POST', headers:{ 'Content-Type':'application/json' },
        body: JSON.stringify({ prompt })
      }).then(res=>res.json()).then(res=>{
        log('Du: ' + prompt);
        if(res.status==='ok') log('NAO: ' + res.command.text);
        else log('Fehler: ' + res.message);
      });
      document.getElementById('userInput').value = '';
    };

    document.getElementById('voiceBtn').onclick = () => {
      log('🔴 Aufnahme...');
      fetch('/voice', { method:'POST' })
        .then(res=>res.json())
        .then(res=>{
          if(res.prompt) {
            log('Transkript: ' + res.prompt);
            fetch('/prompt',{ method:'POST', headers:{ 'Content-Type':'application/json' },
              body: JSON.stringify({ prompt: res.prompt })})
            .then(r=>r.json()).then(r=>{
              if(r.status==='ok') log('NAO: ' + r.command.text);
              else log('Fehler: ' + r.message);
            });
          } else {
            log('Fehler: ' + res.message);
          }
        });
    };
  </script>
</body>
</html>
"""
        return html

    @cherrypy.expose
    def ws(self):
        # WebSocket-Handshake
        cherrypy.request.ws_handler

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def send(self):
        # Legacy-Endpunkt: send
        if not get_single_nao():
            cherrypy.response.status = 503
            return {'status':'error','message':'Kein NAO verbunden'}
        data = cherrypy.request.json
        prompt = data.get('prompt','')
        command = generate_command_from_prompt(prompt)
        broadcast_command(command)
        return {'status':'ok','command':command}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def prompt(self):
        # Web-UI: prompt
        if not get_single_nao():
            cherrypy.response.status = 503
            return {'status':'error','message':'Kein NAO verbunden'}
        data = cherrypy.request.json
        prompt = data.get('prompt','')
        command = generate_command_from_prompt(prompt)
        broadcast_command(command)
        return {'status':'ok','command':command}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def voice(self):
        # Web-UI: voice input
        if not get_single_nao():
            cherrypy.response.status = 503
            return {'status':'error','message':'Kein NAO verbunden'}
        text = voice_input()
        return {'prompt':text}

# Funktionen zum Starten und Stoppen des Servers

def start_webserver(host="0.0.0.0", port=9000):
    cherrypy.config.update({"server.socket_host": host, "server.socket_port": port})
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
    config = {"/ws": {"tools.websocket.on": True, "tools.websocket.handler_cls": CommandWebSocket}}
    cherrypy.tree.mount(Root(), "/", config)
    cherrypy.engine.start()


def stop_webserver():
    cherrypy.engine.exit()
