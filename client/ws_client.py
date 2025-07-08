#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
from websocket import WebSocketApp
from naoqi import ALProxy

# === Konfiguration ===
WS_URL    = "ws://192.168.8.152:9000/ws"  # Dein Server
CLIENT_ID = "nao1"
NAO_IP    = "127.0.0.1"                   # Auf dem NAO: localhost oder seine IP
NAO_PORT  = 9559

# === NAO Proxies ===
tts     = ALProxy("ALTextToSpeech", NAO_IP, NAO_PORT)
motion  = ALProxy("ALMotion",         NAO_IP, NAO_PORT)
posture = ALProxy("ALRobotPosture",   NAO_IP, NAO_PORT)
anim = ALProxy("ALAnimationPlayer", NAO_IP, NAO_PORT)

# Initial-Setup
posture.goToPosture("StandInit", 0.5)
motion.setStiffnesses("Body", 1.0)

def perform_movement(move):
    """Bewegungen basierend auf dem String ausführen."""
    m = move.lower()
    print(u"🤖 perform_movement received:", m)

    if "kopf nicken" in m or "nicken" in m:
        print("  → Kopf nicken")
        motion.angleInterpolation("HeadPitch", -0.3, 1.0, True)
        motion.angleInterpolation("HeadPitch",  0.3, 1.0, True)
        motion.angleInterpolation("HeadPitch",  0.0, 1.0, True)

    elif "kopf neigen" in m or "neigen" in m:
        print("  → Kopf neigen")
        motion.angleInterpolation("HeadYaw", 0.5, 1.0, True)
        motion.angleInterpolation("HeadYaw",-0.5, 1.0, True)
        motion.angleInterpolation("HeadYaw", 0.0, 1.0, True)

    elif "winken" in m:
        print("  → Winken")
        motion.angleInterpolation("RShoulderPitch", -0.5, 0.7, True)
        motion.angleInterpolation("RElbowYaw",       1.0, 0.7, True)
        for _ in range(2):
            motion.angleInterpolation("RElbowRoll", 1.0, 0.5, True)
            motion.angleInterpolation("RElbowRoll", 0.5, 0.5, True)
        posture.goToPosture("StandInit", 0.5)

    elif "arm heben" in m and "heben" in m:
        print("  → Arme heben")
        names  = ["LShoulderPitch","LElbowRoll","RShoulderPitch","RElbowRoll"]
        angles = [0.2, 0.3, -0.2, -0.3]
        times  = [0.5, 0.5, 0.5, 0.5]
        motion.angleInterpolation(names, angles, times, True)
        posture.goToPosture("StandInit", 0.5)
 
    elif "Sprechende Bewegung" in m and "sprechen" in m:
        print("  → sprechen")
        anim.run("animations/Stand/BodyTalk/Speaking/BodyTalk_1")

    elif "hinsetzen" in m and "setzen" in m:
        print("  → hinsetzen")
        posture.goToPosture("Sit", 0.5)

    elif "aufstehen" in m and "stehen" in m:
        print("  → hinsetzen")
        posture.goToPosture("StandInit", 0.5)

    else:
        print("⚠️ Unbekannte Bewegung:", move)

def on_open(ws):
    print("🔗 Verbunden zum Server:", WS_URL)
    register = json.dumps({
        "client_type": "nao",
        "client_id": CLIENT_ID
    })
    ws.send(register)
    print("📢 Registrierung gesendet:", register)

def on_message(ws, msg):
    # Empfang debug
    raw = msg.decode("utf-8") if isinstance(msg, bytes) else msg
    print("⬅️ Roh empfangen:", raw)

    # JSON parsen
    try:
        cmd = json.loads(raw)
    except ValueError as e:
        print("❌ JSON-Parsing-Fehler:", e)
        return

    text     = cmd.get("text", "")
    movement = cmd.get("movement", "")
    delay    = cmd.get("delay", 0)

    # Debug parsed
    print("🔧 Geparstes Kommando:", 
          "text=", repr(text), 
          "movement=", repr(movement), 
          "delay=", delay)

    # Text-to-speech: Unicode → UTF-8 str konvertieren
    if text:
        try:
            text_to_say = text.encode('utf-8') if isinstance(text, unicode) else text
        except NameError:
            text_to_say = text  # falls unicode nicht definiert
        print("🗣 Aufruf tts.say() mit:", text_to_say)
        try:
            tts.say(text_to_say)
        except Exception as e:
            print("❌ tts.say() Fehler:", e)

    # Bewegung
    if movement:
        print("🤖 Aufruf perform_movement() mit:", movement)
        try:
            perform_movement(movement)
        except Exception as e:
            print("❌ perform_movement() Fehler:", e)

    # Verzögerung
    if isinstance(delay, (int, float)) and delay > 0:
        print("⏱ Warte:", delay, "Sekunden")
        time.sleep(delay)

def on_error(ws, error):
    print("❌ WebSocket-Fehler:", error)

def on_close(ws, code, reason=None):
    print("⚠️ Verbindung geschlossen:", code, reason)

if __name__ == "__main__":
    # Reconnect-Loop
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
        print("⏳ Erneuter Verbindungsversuch in 5s…")
        time.sleep(5)
