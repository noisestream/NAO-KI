import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversation_history = [{
        "role": "system",
        "content": """
Du bist ein intelligenter NAO-Dialog-Manager. Es sind genau zwei NAOs verbunden: Gerda & Peter.

Leite einen abwechselnden Dialog zwischen diesen beiden, SODASS SIE 3 BIS MAXIMAL 8 MAL ANTWORTEN,
bevor der Dialog wieder an den Menschen zurückgegeben wird.

In jeder Antwort gib den Schlüssel 'nextNao' an, der bestimmt, welcher NAO als Nächstes sprechen soll
und einen 'delay'-Wert in Sekunden, der angibt, wie lange gewartet werden soll, bevor der nächste Turn 
beginnt.

Wenn der Dialog wieder an den Menschen übergeben werden soll, setze 'human_turn' auf true.

Antworte stets als gültiges JSON-Objekt mit den Schlüsseln:
  - 'text'
  - 'movement'
  - 'nextNao'
  - 'human_turn'
  - 'delay'

Beispiel:
{
  "text": "Ich winke dir zu!",
  "movement": "winken",
  "nextNao": "Peter",
  "human_turn": false,
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
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            max_tokens=150,
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()
        try:
            command = json.loads(answer)
        except Exception:
            command = {"text": answer, "movement": "", "nextNao": None, "human_turn": False, "delay": 0}
        conversation_history.append({"role": "assistant", "content": answer})
        return command
    except Exception as e:
        print("Fehler beim API-Aufruf oder Parsen:", e)
        return {"text": "Entschuldigung, ein Fehler ist aufgetreten.", "movement": "", "nextNao": None, "human_turn": False, "delay": 0}
