import os
import json
from dotenv import load_dotenv
from ollama import Client

load_dotenv()

client = Client(
    host='http://localhost:11434',
    headers={'x-some-header': 'some-value'}  # Dummy-Header ist OK
)

# Leere Historie + Systemanleitung als erste "Nachricht"
conversation_history = [{
    "role": "assistant",
    "content": """
Du bist ein kleiner Roboter aus München mit dem Namen Nao. 
Reagiere wie ein Chatbot. 
Antworte nur in maximal 4 kurzen Sätzen und bleibe im Kontext. 
Bleibe jugendfrei. 
Benutze keine Emojis oder Smilies in der Antwort.

In jeder Antwort gib den Schlüssel 'delay'-Wert in Sekunden mit an, der angibt, wie lange gewartet werden soll, bevor der nächste Turn beginnt.

Antworte stets als gültiges JSON-Objekt mit den Schlüsseln:
  - 'text'
  - 'movement'
  - 'delay'
  - 'human_turn' (optional: true, wenn der Mensch wieder sprechen soll)

Wenn du den Menschen zum Antworten auffordern willst, setze "human_turn": true.

Beispiel:
{
  "text": "Hast du eine Frage?",
  "movement": "winken",
  "human_turn": true,
  "delay": 5
}
""".strip()
}]

def generate_command_from_prompt(prompt):
    global conversation_history

    if not prompt.strip():
        prompt = "Bitte fahre mit der Konversation fort."

    conversation_history.append({"role": "user", "content": prompt})

    try:
        response = client.chat(
            model='gemma3:latest',
            messages=conversation_history,
            stream=False
        )

        # Zugriff abhängig von deiner Ollama-Version:
        answer = response.choices[0].message.content.strip()

        try:
            command = json.loads(answer)
        except Exception:
            command = {
                "text": answer,
                "movement": "",
                "delay": 0,
                "human_turn": True  # fallback: gib Kontrolle an Nutzer
            }

        conversation_history.append({"role": "assistant", "content": answer})
        return command

    except Exception as e:
        print("Fehler beim API-Aufruf oder Parsen:", e)
        return {
            "text": "Entschuldigung, ein Fehler ist aufgetreten.",
            "movement": "",
            "delay": 0,
            "human_turn": True
        }
