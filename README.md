# NAO-chat

## Client (NAO)

1. Verbindung per ssh zu NAO: `ssh nao@<IP-Adresse des Naos>`

2. Bibliothek für Websockets installieren (NAO v6 hat nur Python2)

```bash
pip2 install --user ws4py
```

3. Neue Datei `ws_client.py` auf NAO erstellen und mit `nano` oder `vim` bearbeiten.

4. Code aus [ws_client.py](ws_client.py) in Editor einfügen und anpassen:

- `CLIENT_ID` am Anfang des Codes muss eindeutig sein (z.B. Nummer des NAO)
- `ws_url` am Ende des Codes muss die IP-Adresse des Laptops enthalten

## Server (Laptop)

Anleitung für Mac: (TODO: check on Windows)

1. Im geklonten Projektverzeichnis eine virtuelle Umgebung für Python erstellen und aktivieren:

```bash
python -m venv venv
source venv/bin/activate
```

2. Benötigte Bibliotheken installieren:

```bash
pip install -r requirements.txt
```

3. In `.env` den API-Key von OpenAI eintragen:

```
OPENAI_API_KEY=the_api_key_from_openai
```

## Start

Auf dem Laptop den Server starten:

```bash
python ws_server.py
```

Auf den beteiligten NAOs (mindestens 2) im Terminal den Client starten:

```bash
python2 ws_client.py
```

Nun kann der Server im Terminal Eingaben entgegennehmen.

## Test

```bash
python test/test_nao_client.py Gerda
```
