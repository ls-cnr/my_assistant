#!/usr/bin/env python3
"""
Script per testare il componente Rhubarb Lip Sync.
Riceve un file audio MP3 e genera dati di sincronizzazione labiale in diversi formati.

Uso:
    python test_rhubarb.py input.mp3 [--output output_prefix] [--format json|xml|tsv] [--rhubarb_path path]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def convert_to_wav(mp3_file, temp_dir):
    """Converte un file MP3 in WAV usando ffmpeg, necessario per Rhubarb"""
    wav_file = os.path.join(temp_dir, "temp_audio.wav")
    try:
        subprocess.run(
            ["ffmpeg", "-i", mp3_file, "-ar", "44100", wav_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Convertito {mp3_file} in WAV")
        return wav_file
    except subprocess.CalledProcessError as e:
        print(f"Errore durante la conversione del file MP3: {e}")
        print(f"Output di errore: {e.stderr.decode()}")
        sys.exit(1)
    except FileNotFoundError:
        print("ffmpeg non trovato. Assicurati che ffmpeg sia installato e disponibile nel PATH.")
        sys.exit(1)


def run_rhubarb(wav_file, output_file, output_format, rhubarb_path):
    """Esegue Rhubarb Lip Sync sul file WAV per generare i dati di sincronizzazione"""
    try:
        # Costruisci il comando Rhubarb
        cmd = [
            rhubarb_path,
            "-f", output_format,
            "-o", output_file,
            wav_file
        ]

        # Esegui Rhubarb
        print(f"Esecuzione di Rhubarb: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"Rhubarb completato con successo. Output salvato in: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di Rhubarb: {e}")
        print(f"Output di errore: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Eseguibile Rhubarb non trovato in: {rhubarb_path}")
        print("Assicurati che il percorso sia corretto e che l'eseguibile abbia i permessi di esecuzione.")
        return False


def analyze_output(output_file, output_format):
    """Analizza e mostra un riepilogo dell'output generato da Rhubarb"""
    try:
        if output_format == "json":
            with open(output_file, 'r') as f:
                data = json.load(f)
                mouth_cues = data.get("mouthCues", [])
                print(f"\nAnalisi dell'output JSON:")
                print(f"  - Durata totale: {data.get('metadata', {}).get('duration', 'N/A')} secondi")
                print(f"  - Numero di mouth cues: {len(mouth_cues)}")
                print(f"  - Esempio dei primi 3 mouth cues:")
                for i, cue in enumerate(mouth_cues[:3]):
                    print(f"    {i+1}. Da {cue.get('start')} a {cue.get('end')}: {cue.get('value')}")

        elif output_format == "tsv":
            with open(output_file, 'r') as f:
                lines = f.readlines()
                print(f"\nAnalisi dell'output TSV:")
                print(f"  - Numero di linee: {len(lines)}")
                print(f"  - Esempio delle prime 3 linee:")
                for i, line in enumerate(lines[:3]):
                    print(f"    {i+1}. {line.strip()}")

        elif output_format == "xml":
            # Per semplicità, mostro solo il numero di righe e alcune righe iniziali
            with open(output_file, 'r') as f:
                lines = f.readlines()
                print(f"\nAnalisi dell'output XML:")
                print(f"  - Numero di linee: {len(lines)}")
                print(f"  - Prime 5 righe:")
                for i, line in enumerate(lines[:5]):
                    print(f"    {i+1}. {line.strip()}")

        return True
    except Exception as e:
        print(f"Errore durante l'analisi dell'output: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Testa Rhubarb Lip Sync con un file audio MP3")
    parser.add_argument("input_file", help="File audio MP3 di input")
    parser.add_argument("--output", help="Prefisso del file di output (senza estensione)", default="output_lipsync")
    parser.add_argument("--format", choices=["json", "xml", "tsv"], default="json",
                        help="Formato di output (default: json)")
    parser.add_argument("--rhubarb_path", help="Percorso all'eseguibile di Rhubarb",
                        default="./bin/rhubarb/rhubarb")

    args = parser.parse_args()

    # Verifica esistenza del file di input
    if not os.path.isfile(args.input_file):
        print(f"File di input non trovato: {args.input_file}")
        sys.exit(1)

    # Verifica esistenza dell'eseguibile Rhubarb
    rhubarb_exec = args.rhubarb_path
    if not os.path.isfile(rhubarb_exec):
        # Prova percorsi alternativi comuni
        alternatives = [
            "./rhubarb",
            "./bin/rhubarb.exe",
            "./rhubarb.exe",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin/rhubarb"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin/rhubarb.exe")
        ]

        for alt in alternatives:
            if os.path.isfile(alt):
                rhubarb_exec = alt
                print(f"Trovato eseguibile Rhubarb in: {alt}")
                break
        else:
            print(f"Eseguibile Rhubarb non trovato. Percorsi verificati:")
            print(f"  - {args.rhubarb_path}")
            for alt in alternatives:
                print(f"  - {alt}")
            sys.exit(1)

    # Crea directory temporanea
    with tempfile.TemporaryDirectory() as temp_dir:
        # Converti MP3 in WAV (formato richiesto da Rhubarb)
        wav_file = convert_to_wav(args.input_file, temp_dir)

        # Costruisci il percorso del file di output
        output_file = f"{args.output}.{args.format}"

        # Esegui Rhubarb
        if run_rhubarb(wav_file, output_file, args.format, rhubarb_exec):
            # Analizza l'output
            analyze_output(output_file, args.format)
            print("\nTest completato con successo!")
        else:
            print("\nTest fallito.")
            sys.exit(1)


if __name__ == "__main__":
    main()
