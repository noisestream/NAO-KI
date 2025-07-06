#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
from websocket import WebSocketApp

# Adresse deines WebSocket-Servers
WS_URL = "ws://192.168.8.152:9000/ws"

# Eindeutige ID für deinen NAO
CLIENT_ID = "nao1"

def on_open(ws):
    print("Verbunden zum Server:", WS_URL)
    register_msg = {
        "client_type": "nao",
        "client_id": CLIENT_ID
    }
    msg_str = json.dumps(register_msg)
    ws.send(msg_str)
    print(">> Registrierungsnachricht gesendet:", msg_str)

def on_message(ws, m):
    raw = m if isinstance(m, unicode) else m.decode("utf-8")
    print("<< Roh empfangen:", raw)
    try:
        cmd = json.loads(raw)
    except ValueError as e:
        print("❌ JSON-Parsing-Fehler:", e)
        return

    text = cmd.get("text")
    movement = cmd.get("movement")
    delay = cmd.get("delay", 0)

    # Validierung
    if not isinstance(text, basestring) or not isinstance(movement, basestring):
        print("❌ Ungültiger Befehl:", cmd)
        return

    print("✅ Befehl:", cmd)
    # Hier die NAO-API-Aufrufe einfügen, z.B.:
    # nao_proxy.say(text)
    # nao_proxy.move(movement)
    print("-> Text: %s | Bewegung: %s | Verzögerung: %ss" % (text, movement, delay))

def on_error(ws, error):
    print("❌ WebSocket-Fehler:", error)

def on_close(ws, code, reason=None):
    print("⚠️ Verbindung geschlossen (code=%s, reason=%s)" % (code, reason))

if __name__ == "__main__":
    # Stelle sicher, dass websocket-client installiert ist:
    # sudo pip install websocket-client
    while True:
        try:
            ws = WebSocketApp(
                WS_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception as e:
            print("❌ Laufzeitfehler:", e)
        print("⏳ Erneuter Verbindungsversuch in 5 Sekunden...")
        time.sleep(5)
