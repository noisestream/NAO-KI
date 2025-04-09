#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import json
from ws4py.client.threadedclient import WebSocketClient
from naoqi import ALProxy

# Eindeutige Client-ID – passe diesen Wert individuell an
CLIENT_ID = "Gerda" # Name des NAOs, z.B. "Gerda" oder "Peter"

class NAOWebSocketClient(WebSocketClient):
    def opened(self):
        print "Verbindung geöffnet:", self.peer_address
        # Registrierungsnachricht an den Server senden
        self.send(json.dumps({"client_id": CLIENT_ID}))

    def closed(self, code, reason=None):
        print "Verbindung geschlossen: Code =", code, "Reason =", reason

    def received_message(self, m):
        print "Nachricht erhalten:", m.data
        try:
            # Dekodiere die eingehende Nachricht als UTF-8 und parse sie als JSON
            command = json.loads(m.data.decode("utf-8"))
            if "text" in command:
                self.execute_text(command["text"])
            if "movement" in command:
                self.execute_motion(command["movement"])
        except Exception as e:
            print "Fehler beim Verarbeiten der Nachricht:", e

    def execute_text(self, text):
        try:
            tts = ALProxy("ALTextToSpeech", "127.0.0.1", 9559)
            # Stelle sicher, dass 'text' ein Unicode-Objekt ist
            if not isinstance(text, unicode):
                text = text.decode("utf-8", "ignore")
            text_utf8 = text.encode("utf-8", "ignore")
            tts.say(text_utf8)
            print "Sprachausgabe ausgeführt:", text_utf8
        except Exception as e:
            print "Fehler bei TTS:", e

    def execute_motion(self, motion_command):
        try:
            motion = ALProxy("ALMotion", "127.0.0.1", 9559)
            if motion_command == "nicken":
                motion.angleInterpolation("HeadPitch", [0.2, -0.2, 0.0],
                                          [0.5, 1.0, 1.5], True)
                print "Bewegung ausgeführt: nicken"
            elif motion_command == "winken":
                motion.angleInterpolation("LShoulderPitch", [1.2, 0.7, 1.2, 0.7, 1.2],
                                          [0.5, 1.0, 1.5, 2.0, 2.5], True)
                print "Bewegung ausgeführt: winken"
            elif motion_command == "freudig":
                # Beispiel: Beide Schultern leicht heben
                motion.angleInterpolation(["RShoulderPitch", "LShoulderPitch"],
                                          [-0.2, -0.2], [1.0, 1.0], True)
                print "Bewegung ausgeführt: freudig"
            elif motion_command == "shake_head":
                motion.angleInterpolation("HeadYaw", [0.5, -0.5, 0.0],
                                          [0.5, 1.5, 2.0], True)
                print "Bewegung ausgeführt: shake_head"
            else:
                print "Keine definierte Bewegung für:", motion_command
        except Exception as e:
            print "Fehler bei Bewegung:", e

if __name__ == '__main__':
    # Setze hier die WebSocket-URL deines Servers; ersetze <Laptop-IP> durch die tatsächliche IP (z.B. "192.168.1.50")
    ws_url = 'ws://<Laptop-IP>:9000/ws'
    
    try:
        ws = NAOWebSocketClient(ws_url, protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
