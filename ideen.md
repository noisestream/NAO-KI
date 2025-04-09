Die nächste Erweiterung sollte eine „echte“ Unterhaltung zwischen den NAOs 
ermöglichen, d.h. jeder NAO hat seine eigene ChatGPT-Session mit Eingaben
des anderen NAOs. 

Aktuell funktioniert die Verzögerung zwischen den sprechenden NAOs nicht
gut und die Bedienung im Terminal könnte komfortabler sein.

## Ideensammlung

- NAOs mit unterschiedlichen Stimmlagen
- Animationen und andere Dinge einbauen, siehe http://doc.aldebaran.com/2-8/naoqi/index.html
- Mehr Kommandos: Gesten, Laufen, Augen, usw.
- Kann ChatGPT bestimmte Körperpositionen generieren?
- Benutzeroberfläche als Webanwendung?

## Code modernisieren

- [Starlette](https://www.starlette.io) oder andere Bibliothek für Websocket anstatt veraltetes `CherryPy`
- [Sounddevice](https://github.com/spatialaudio/python-sounddevice/) anstatt veraltetes `PyAudio`
