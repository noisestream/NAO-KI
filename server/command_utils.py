# server/command_utils.py
import json
import re
import time
import threading
import queue

# Globale Referenz für den einzelnen NAO-Client
single_nao_client = None

# Thread-sichere Queue für alle zu sendenden Nachrichten
_message_queue = queue.Queue()

def set_single_nao(client):
    global single_nao_client
    single_nao_client = client
    if client:
        addr = getattr(client, 'peer_address', None)
        print("NAO-Client gesetzt:", addr)
    else:
        print("NAO-Client zurückgesetzt")

def get_single_nao():
    return single_nao_client

def _sender_loop():
    while True:
        client, message = _message_queue.get()
        try:
            client.send(message)
        except Exception as e:
            print("❌ Fehler beim Senden an NAO:", e)

# Starte den Sender-Thread einmalig
_thread = threading.Thread(target=_sender_loop, daemon=True)
_thread.start()

def broadcast_command(command):
    nao = single_nao_client
    if not nao:
        print("⚠️ Kein NAO verbunden.")
        return

    # Füge msg_id hinzu, wenn gewünscht
    command["msg_id"] = int(time.time())
    message = json.dumps(command)

    # Enqueue, wird dann seriell im _sender_loop verschickt
    _message_queue.put((nao, message))
    print("📝 Befehl zu Queue hinzugefügt:", message)

def calculate_delay(text, min_delay=5, words_per_second=1.9, pause_per_sentence=0.6):
    word_count = len(re.findall(r"\w+", text))
    sentence_count = len(re.findall(r"[.!?]", text))
    est_word = word_count / words_per_second
    est_pause = sentence_count * pause_per_sentence
    return max(min_delay, est_word + est_pause)
