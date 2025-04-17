#!/usr/bin/env python3
"""
Script semplificato per testare Qwen-Audio-Chat, adattato dal demo web ufficiale.
Usa l'approccio documentato nel tutorial ufficiale per una migliore compatibilità.
"""

import argparse
import os
import logging
import time
import librosa
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Test semplificato per Qwen-Audio-Chat')
    parser.add_argument('-a', '--audio', type=str, required=True,
                        help='Percorso del file audio da processare')
    parser.add_argument('-p', '--prompt', type=str, required=True,
                        help='Prompt testuale da inviare al modello')
    parser.add_argument('-o', '--output', type=str, default='qwen_response.txt',
                        help='Nome del file di output (default: qwen_response.txt)')
    parser.add_argument('-c', '--checkpoint', type=str, default="Qwen/Qwen-Audio-Chat",
                        help='Percorso del checkpoint del modello (default: Qwen/Qwen-Audio-Chat)')
    parser.add_argument('--cpu-only', action='store_true',
                        help='Esegui solo su CPU')

    args = parser.parse_args()

    # Verifica che il file audio esista
    if not os.path.exists(args.audio):
        logger.error(f"Il file audio '{args.audio}' non esiste")
        return

    try:
        # Carica tokenizer e modello seguendo esattamente l'approccio del tutorial
        logger.info(f"Caricamento del tokenizer da {args.checkpoint}...")
        tokenizer = AutoTokenizer.from_pretrained(
            args.checkpoint, trust_remote_code=True
        )

        # Imposta device_map in base all'opzione cpu-only
        device_map = "cpu" if args.cpu_only else "auto"

        logger.info(f"Caricamento del modello da {args.checkpoint} su {device_map}...")
        model = AutoModelForCausalLM.from_pretrained(
            args.checkpoint,
            device_map=device_map,
            trust_remote_code=True
        ).eval()

        # Carica la configurazione di generazione dal checkpoint
        model.generation_config = GenerationConfig.from_pretrained(
            args.checkpoint, trust_remote_code=True
        )

        # Usa from_list_format come nell'esempio ufficiale
        logger.info(f"Preparazione dell'input con il file audio {args.audio}...")
        query = tokenizer.from_list_format([
            {'audio': args.audio},
            {'text': args.prompt},
        ])

        # Esegui la chat senza history (prima interazione)
        logger.info("Generazione della risposta...")
        start_time = time.time()
        response, history = model.chat(tokenizer, query=query, history=None)
        end_time = time.time()

        logger.info(f"Risposta generata in {end_time - start_time:.2f} secondi")
        logger.info(f"Risposta: {response}")

        # Salva la risposta nel file di output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(response)

        logger.info(f"Risposta salvata in '{args.output}'")

    except Exception as e:
        logger.error(f"Errore durante l'esecuzione: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    main()
