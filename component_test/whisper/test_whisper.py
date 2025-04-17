#!/usr/bin/env python3
"""
Script per trascrivere audio usando il modello Whisper di OpenAI,
che è più leggero e funziona anche su hardware con risorse limitate.
"""

import argparse
import os
import logging
import torch
import time
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transcribe_audio(audio_file, output_file, model_size="small"):
    """
    Trascrive un file audio usando Whisper e salva la trascrizione in un file.

    Args:
        audio_file (str): Percorso del file audio
        output_file (str): Percorso dove salvare la trascrizione
        model_size (str): Dimensione del modello Whisper (tiny, base, small, medium, large)
    """
    try:
        # Scegli il dispositivo adatto
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Utilizzo del dispositivo: {device}")

        # Carica il modello Whisper e il processor
        model_name = f"openai/whisper-{model_size}"
        logger.info(f"Caricamento del modello {model_name}...")

        processor = WhisperProcessor.from_pretrained(model_name)
        model = WhisperForConditionalGeneration.from_pretrained(model_name).to(device)

        # Importa librosa per caricare l'audio
        import librosa

        logger.info(f"Caricamento del file audio {audio_file}...")
        # Carica l'audio con librosa
        audio_data, sampling_rate = librosa.load(audio_file, sr=16000)

        # Prepara l'input per il modello
        input_features = processor(audio_data, sampling_rate=16000, return_tensors="pt").input_features.to(device)

        # Genera la trascrizione
        logger.info("Generazione della trascrizione...")
        start_time = time.time()

        with torch.no_grad():
            predicted_ids = model.generate(input_features)

        # Decodifica la trascrizione
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
        end_time = time.time()

        logger.info(f"Trascrizione generata in {end_time - start_time:.2f} secondi")

        # Estrai la trascrizione dal batch
        transcription_text = transcription[0]
        logger.info(f"Trascrizione: {transcription_text}")

        # Salva la trascrizione nel file di output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transcription_text)

        logger.info(f"Trascrizione salvata in '{output_file}'")

        return transcription_text

    except Exception as e:
        logger.error(f"Errore durante la trascrizione: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def main():
    parser = argparse.ArgumentParser(description='Trascrizione audio con Whisper')
    parser.add_argument('-a', '--audio', type=str, required=True,
                        help='Percorso del file audio da trascrivere')
    parser.add_argument('-o', '--output', type=str, default='whisper_transcript.txt',
                        help='Nome del file di output per la trascrizione (default: whisper_transcript.txt)')
    parser.add_argument('-m', '--model', type=str, default="small",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help='Dimensione del modello Whisper da utilizzare (default: small)')

    args = parser.parse_args()

    # Verifica che il file audio esista
    if not os.path.exists(args.audio):
        logger.error(f"Il file audio '{args.audio}' non esiste")
        return

    try:
        transcribe_audio(args.audio, args.output, args.model)
    except Exception as e:
        logger.error(f"Errore nell'esecuzione del test: {str(e)}")

if __name__ == '__main__':
    main()
