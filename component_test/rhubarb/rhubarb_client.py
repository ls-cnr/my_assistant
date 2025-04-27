#!/usr/bin/env python3
"""
Script per richiedere la riproduzione di un file audio con sincronizzazione labiale in Unity
Uso: python rhubarb_client.py --name filename [--url http://localhost:8080/avatar/speak]
"""

import argparse
import requests
import json
import sys

def request_speech(url, file_name):
    """
    Richiede a Unity di riprodurre un file audio con sincronizzazione labiale

    Args:
        url: URL dell'endpoint speak
        file_name: Nome del file da riprodurre (senza estensione)

    Returns:
        bool: True se la richiesta ha avuto successo, False altrimenti
    """
    # Costruisci l'URL completo con il parametro del nome del file
    full_url = f"{url}?file={file_name}"

    print(f"Richiesta di riproduzione del file '{file_name}'...")

    try:
        # Invia la richiesta GET
        response = requests.get(full_url)

        # Verifica la risposta
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print(f"Successo: {result.get('message')}")
                return True
            else:
                print(f"Errore dal server: {result.get('message', 'Nessun messaggio di errore')}")
        else:
            print(f"Errore HTTP: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Errore di connessione: {e}")
    except json.JSONDecodeError:
        print("Errore: Risposta non valida dal server")
    except Exception as e:
        print(f"Errore imprevisto: {e}")

    return False

def main():
    # Configurazione degli argomenti da linea di comando
    parser = argparse.ArgumentParser(description='Richiede la riproduzione di un file audio con sincronizzazione labiale in Unity')
    parser.add_argument('--name', required=True,
                        help='Nome del file da riprodurre (senza estensione)')
    parser.add_argument('--url', default='http://localhost:8080/avatar/speak',
                        help='URL dell\'endpoint speak (default: http://localhost:8080/avatar/speak)')

    args = parser.parse_args()

    # Invia la richiesta di riproduzione
    success = request_speech(args.url, args.name)

    # Esci con codice appropriato
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
