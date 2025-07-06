import time
from audio_utils import voice_input
from openai_utils import generate_command_from_prompt
from command_utils import broadcast_command, get_single_nao
from dialog_loop import conversation_loop

def conversation_manager():
    """
    Hauptmanagerschleife für die Konversation.
    Wählt einmalig den Eingabemodus (Text oder Voice) am Start aus und behält ihn bei.
    Fährt dann automatisch zwischen menschlichem und NAO-Modus fort, bis 'exit' eingegeben wird.
    """
    mode = None  # 't' oder 'v'
    while True:
        # Eingabemodus einmalig abfragen
        if mode is None:
            selection = input("Wähle Eingabemodus ('t' für Text, 'v' für Voice, 'exit' zum Beenden): ").strip().lower()
            if selection == 'exit':
                print("Beende Konversation.")
                break
            if selection in ('t', 'v'):
                mode = selection
            else:
                print("Ungültige Auswahl. Bitte 't', 'v' oder 'exit' eingeben.")
                continue

        # Prüfen, ob ein NAO verbunden ist
        if not get_single_nao():
            print("❌ Kein NAO verbunden. Warte...")
            time.sleep(1)
            continue

        # Menschen-Prompt entsprechend Modus
        if mode == 'v':
            prompt = voice_input()
        else:
            prompt = input("Gib deine Texteingabe ein (oder 'exit' zum Beenden): ").strip()
            if prompt.lower() == 'exit':
                print("Beende Konversation.")
                break

        # Erster LLM-Aufruf für menschliche Eingabe
        print("Sende Anfrage an LLM...")
        command = generate_command_from_prompt(prompt)
        broadcast_command(command)

        # Automatischen Dialog nur starten, wenn das Modell weiterführen will
        if not command.get("human_turn", False) and not command.get("end_conversation", False):
            conversation_loop()

    # Ende while True

if __name__ == '__main__':
    conversation_manager()
