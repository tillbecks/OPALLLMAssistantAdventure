from secret_keys import STD_LOG_PATH
import os
import datetime

LOG_FILENAME = None

def initialize_logger(filename=STD_LOG_PATH):
    """Erstellt oder setzt die Log-Datei zurück."""
    global LOG_FILENAME
    LOG_FILENAME = filename
    with open(LOG_FILENAME, "w") as f:
        f.write(f"Log gestartet am {datetime.datetime.now()}\n")

def log(message):
    """Fügt eine Log-Nachricht mit Zeitstempel hinzu."""
    if LOG_FILENAME is None:
        raise RuntimeError("Logger wurde nicht initialisiert. Bitte initialize_logger() aufrufen.")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILENAME, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def get_logs():
    """Liest den gesamten Inhalt der Log-Datei und gibt ihn zurück."""
    if LOG_FILENAME is None:
        raise RuntimeError("Logger wurde nicht initialisiert. Bitte initialize_logger() aufrufen.")
    with open(LOG_FILENAME, "r") as f:
        return f.read()

# Beispiel zur Verwendung
if __name__ == "__main__":
    initialize_logger()
    log("Programm gestartet.")
    log("Eine weitere Log-Nachricht.")
    print("Log-Inhalt:")
    print(get_logs())
