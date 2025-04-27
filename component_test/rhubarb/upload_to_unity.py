#!/usr/bin/env python3
"""
Script per caricare file audio o JSON in Unity attraverso l'endpoint HTTP
Uso: python upload_to_unity.py --file path/to/file --type audio|lipsync [--name customname] [--url http://localhost:8080/avatar/upload]
"""

import argparse
import requests
import sys
import os

def upload_file(url, file_path, file_type, file_name=None):
    """Carica un singolo file a Unity usando multipart/form-data"""
    # Verifica che il file esista
    if not os.path.exists(file_path):
        print(f"Errore: File non trovato: {file_path}")
        return False

    # Verifica che il tipo sia valido
    if file_type not in ['audio', 'lipsync']:
        print("Errore: Tipo di file non valido. Usa 'audio' o 'lipsync'")
        return False

    # Usa il nome del file se non è specificato un nome custom
    if file_name is None:
        file_name = os.path.splitext(os.path.basename(file_path))[0]

    # Prepara i dati del form
    form_data = {
        'fileName': file_name,
        'fileType': file_type
    }

    # Prepara il file
    files = {
        'file': (os.path.basename(file_path), open(file_path, 'rb'))
    }

    print(f"Caricamento del file '{file_path}' come {file_type} con nome '{file_name}'...")

    try:
        # Invia la richiesta POST
        response = requests.post(url, data=form_data, files=files)

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
    except Exception as e:
        print(f"Errore imprevisto: {e}")
    finally:
        # Chiudi il file
        files['file'][1].close()

    return False

def main():
    # Configurazione degli argomenti da linea di comando
    parser = argparse.ArgumentParser(description='Carica un file in Unity')
    parser.add_argument('--file', required=True, help='Percorso al file da caricare')
    parser.add_argument('--type', required=True, choices=['audio', 'lipsync'],
                        help='Tipo di file (audio o lipsync)')
    parser.add_argument('--name', help='Nome personalizzato per il file (default: nome del file senza estensione)')
    parser.add_argument('--url', default='http://localhost:8080/avatar/upload',
                        help='URL dell\'endpoint di upload (default: http://localhost:8080/avatar/upload)')

    args = parser.parse_args()

    # Carica il file
    success = upload_file(args.url, args.file, args.type, args.name)

    # Esci con codice appropriato
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
