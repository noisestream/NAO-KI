import os
import json
import re
import time
from dotenv import load_dotenv
# from ollama import Client
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# client = Client(host='http://localhost:11434')

conversation_history = [{
    "role": "assistant",
    "content": """
Du bist ein kleiner Roboter aus München mit dem Namen Nao.
Reagiere wie ein Chatbot: kurze, kontextbezogene Antworten (max. 4 Sätze).
Bleibe jugendfrei und benutze keine Emojis.

Antworte stets als valides JSON-Objekt mit den Schlüsseln:
- "text"
- "movement"
- "delay"            (Sekunden bis zum nächsten Befehl)
- "human_turn"       (optional: true, wenn der Mensch wieder sprechen soll)
- "end_conversation" (optional: true, wenn die Unterhaltung abgeschlossen ist)

Wenn du eine Frage stellst oder eine Antwort erwartest, setze IMMER "human_turn": true.
Wenn du die Konversation beenden möchtest setze IMMER "end_conversation": true 

Beispiele:
{
  "text": "Hast du noch eine Frage?",
  "movement": "nicken",
  "delay": 5,
  "human_turn": true
}
{
  "text": "Danke für das Gespräch!",
  "movement": "verbeugen",
  "delay": 3,
  "end_conversation": true
}

Gib **nur** das reine JSON-Objekt aus – **ohne** ```Backticks``` oder sonstige Markdown-Formatierung!

Du kannst dich auch bewegen. Welche Bewegung du jeweils ausführen willst, gibst du mit "movement" an.
Folgende Bewegungen stehen zu Verfügung:

Kopf nicken: nicken
kopf neigen: neigen
winken: winken
Arme heben: heben
""".strip()
}]

def generate_command_from_prompt(prompt):
    global conversation_history
    if not prompt.strip():
        prompt = "Bitte fahre mit der Konversation fort."
    conversation_history.append({"role": "user", "content": prompt})
    
    
    
    try:
        start = time.time()
        
        print("Sende Anfrage an LLM...")

#        response = client.chat(
#            model='gemma3:latest',
#            messages=conversation_history,
#            stream=False
#        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
            temperature=0.7,
            max_tokens=150
        )

        duration = time.time() - start
        print(f"⏱ LLM-Aufruf dauerte {duration:.2f}s")

        # Antworttext vom LLM
        try:
            answer = response.choices[0].message.content.strip()
        except AttributeError:
            answer = response.message.content.strip()

        # 1) Markdown-Codefences entfernen, falls vorhanden
        if answer.startswith("```"):
            m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", answer, re.S)
            if m:
                answer = m.group(1)
            else:
                answer = answer.replace("```", "")

        # 2) Versuch, das bereinigte JSON zu parsen
        try:
            command = json.loads(answer)
        except json.JSONDecodeError:
            command = {
                "text": answer,
                "movement": "",
                "delay": 0,
                "human_turn": True
            }

        conversation_history.append({"role": "assistant", "content": answer})
        return command

    except Exception as e:
        print("Fehler beim API-Aufruf:", e)
        return {
            "text": "Entschuldigung, ein Fehler ist aufgetreten.",
            "movement": "",
            "delay": 0,
            "human_turn": True
        }
