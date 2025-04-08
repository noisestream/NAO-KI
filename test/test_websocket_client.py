import requests
import json
import time

def test_register_client():
    data = {"client_id": "client_123"}
    response = requests.post("http://localhost:9000/", json=data)
    print("Antwort:", response.text)

def test_send_message():
    data = {"message": "Hallo Server"}
    response = requests.post("http://localhost:9000/", json=data)
    print("Antwort:", response.text)

def test_invalid_json():
    headers = {"Content-Type": "application/json"}
    response = requests.post("http://localhost:9000/", data="{this is not: valid json", headers=headers)
    print("Antwort:", response.text)

def test_register_multiple():
    for i in range(3):
        data = {"client_id": f"client_{i}"}
        response = requests.post("http://localhost:9000/", json=data)
        print(f"Antwort {i}:", response.text)
        time.sleep(0.2)

def test_close_connection():
    print("❌ HTTP-Verbindungen sind kurzlebig und müssen nicht explizit geschlossen werden.")

# Menüdefinition
TESTS = {
    "1": ("Client registrieren", test_register_client),
    "2": ("Nachricht ohne client_id", test_send_message),
    "3": ("Ungültiges JSON senden", test_invalid_json),
    "4": ("Mehrere Clients registrieren", test_register_multiple),
    "5": ("Verbindung schließen (nur Hinweis)", test_close_connection)
}

if __name__ == "__main__":
    print("\n🔌 Verbindung via HTTP vorbereitet.\n")
    print("Wähle einen Testfall aus:")
    for key, (desc, _) in TESTS.items():
        print(f" {key}. {desc}")
    choice = input("\nNummer eingeben und Enter drücken: ").strip()

    if choice in TESTS:
        _, test_func = TESTS[choice]
        test_func()
    else:
        print("❌ Ungültige Auswahl.")
