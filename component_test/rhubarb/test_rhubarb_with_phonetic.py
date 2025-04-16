#!/usr/bin/env python3
"""
Script per testare il componente Rhubarb Lip Sync con il riconoscitore fonetico.
Questo script è ottimizzato per audio in lingue non inglesi (es. italiano).

Uso:
    python test_rhubarb_with_phonetic.py input.mp3 [--output output_prefix] [--format json|xml|tsv] [--rhubarb_path path]
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


def run_rhubarb_with_phonetic(wav_file, output_file, output_format, rhubarb_path, dialog_file=None):
    """
    Esegue Rhubarb Lip Sync sul file WAV utilizzando il riconoscitore fonetico
    per generare i dati di sincronizzazione labiale
    """
    try:
        # Costruisci il comando Rhubarb con il riconoscitore fonetico
        cmd = [
            rhubarb_path,
            "-f", output_format,  # Formato di output
            "-r", "phonetic",     # Usa il riconoscitore fonetico per lingue non inglesi
            "-o", output_file,    # File di output
        ]

        # Aggiungi file di dialogo se specificato
        if dialog_file:
            cmd.extend(["-d", dialog_file])

        # Aggiungi il file WAV alla fine
        cmd.append(wav_file)

        # Esegui Rhubarb
        print(f"Esecuzione di Rhubarb con riconoscitore fonetico: {' '.join(cmd)}")
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
                print(f"  - Distribuzione delle forme labiali:")

                # Conta le occorrenze di ogni forma labiale
                mouth_shapes = {}
                for cue in mouth_cues:
                    shape = cue.get('value')
                    if shape in mouth_shapes:
                        mouth_shapes[shape] += 1
                    else:
                        mouth_shapes[shape] = 1

                for shape, count in sorted(mouth_shapes.items()):
                    print(f"    {shape}: {count} occorrenze")

                # Mostra alcuni esempi
                print(f"  - Esempio dei primi 5 mouth cues:")
                for i, cue in enumerate(mouth_cues[:5]):
                    print(f"    {i+1}. Da {cue.get('start')} a {cue.get('end')}: {cue.get('value')}")

        elif output_format == "tsv":
            with open(output_file, 'r') as f:
                lines = f.readlines()
                print(f"\nAnalisi dell'output TSV:")
                print(f"  - Numero di linee: {len(lines)}")

                # Conta le occorrenze di ogni forma labiale
                mouth_shapes = {}
                for line in lines:
                    if line.strip():
                        parts = line.strip().split('\t')
                        if len(parts) >= 2:
                            shape = parts[1]
                            if shape in mouth_shapes:
                                mouth_shapes[shape] += 1
                            else:
                                mouth_shapes[shape] = 1

                print(f"  - Distribuzione delle forme labiali:")
                for shape, count in sorted(mouth_shapes.items()):
                    print(f"    {shape}: {count} occorrenze")

                print(f"  - Esempio delle prime 5 linee:")
                for i, line in enumerate(lines[:5]):
                    print(f"    {i+1}. {line.strip()}")

        elif output_format == "xml":
            # Per XML mostriamo statistiche più semplici
            with open(output_file, 'r') as f:
                content = f.read()

                # Contiamo le occorrenze di ogni forma labiale
                mouth_shapes = {}
                import re
                cues = re.findall(r'<mouthCue start="[^"]+" end="[^"]+">(.*?)</mouthCue>', content)

                for shape in cues:
                    if shape in mouth_shapes:
                        mouth_shapes[shape] += 1
                    else:
                        mouth_shapes[shape] = 1

                print(f"\nAnalisi dell'output XML:")
                print(f"  - Numero totale di mouth cues: {len(cues)}")
                print(f"  - Distribuzione delle forme labiali:")
                for shape, count in sorted(mouth_shapes.items()):
                    print(f"    {shape}: {count} occorrenze")

        return True
    except Exception as e:
        print(f"Errore durante l'analisi dell'output: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Testa Rhubarb Lip Sync con il riconoscitore fonetico per audio in italiano o altre lingue non inglesi")
    parser.add_argument("input_file", help="File audio MP3 di input")
    parser.add_argument("--output", help="Prefisso del file di output (senza estensione)", default="output_phonetic")
    parser.add_argument("--format", choices=["json", "xml", "tsv"], default="json",
                        help="Formato di output (default: json)")
    parser.add_argument("--rhubarb_path", help="Percorso all'eseguibile di Rhubarb",
                        default="./bin/rhubarb/rhubarb")
    parser.add_argument("--dialog", help="File di testo con il dialogo trascritto (opzionale, migliora la precisione)")
    parser.add_argument("--extended_shapes", help="Forme labiali estese da utilizzare (es. 'GHX')", default="GHX")

    args = parser.parse_args()

    # Verifica esistenza del file di input
    if not os.path.isfile(args.input_file):
        print(f"File di input non trovato: {args.input_file}")
        sys.exit(1)

    # Verifica esistenza del file di dialogo se specificato
    if args.dialog and not os.path.isfile(args.dialog):
        print(f"File di dialogo non trovato: {args.dialog}")
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

        # Esegui Rhubarb con il riconoscitore fonetico
        if run_rhubarb_with_phonetic(wav_file, output_file, args.format, rhubarb_exec, args.dialog):
            # Analizza l'output
            analyze_output(output_file, args.format)
            print("\nTest completato con successo!")
            print(f"\nConsiglio per l'integrazione:")
            print(f"1. Per integrare questo output con Ready Player Me, utilizza la mappatura tra i mouth shapes di Rhubarb e i visemi di Oculus LipSync")
            print(f"2. Sfrutta i timestamp per sincronizzare l'audio con l'animazione dell'avatar")
        else:
            print("\nTest fallito.")
            sys.exit(1)


if __name__ == "__main__":
    main()
