import json
import re
import time

# Globale Referenz für den einzelnen NAO-Client
single_nao_client = None

def set_single_nao(client):
    """
    Setzt oder entfernt den registrierten NAO-Client.
    Wenn client None ist, wird der interne Verweis zurückgesetzt.
    """
    global single_nao_client
    single_nao_client = client
    if client:
        addr = getattr(client, 'peer_address', None)
        print("NAO-Client gesetzt:", addr)
    else:
        print("NAO-Client zurückgesetzt")


def get_single_nao():
    return single_nao_client


def broadcast_command(command):
    nao = single_nao_client
    if not nao:
        print("⚠️ Kein NAO verbunden.")
        return

    # Eindeutige ID per Timestamp
    command["msg_id"] = int(time.time())
    message = json.dumps(command)
    try:
        nao.send(message)
        print("✅ Befehl gesendet an NAO:", message)
    except Exception as e:
        print("❌ Fehler beim Senden an NAO:", e)


def calculate_delay(text, min_delay=5, words_per_second=1.9, pause_per_sentence=0.6):
    word_count = len(re.findall(r"\w+", text))
    sentence_count = len(re.findall(r"[.!?]", text))
    estimated_word_duration = word_count / words_per_second
    estimated_pause_duration = sentence_count * pause_per_sentence
    total_duration = estimated_word_duration + estimated_pause_duration
    return max(min_delay, total_duration)