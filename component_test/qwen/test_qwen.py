#!/usr/bin/env python3
"""
Script per testare il modello Qwen2-Audio.
Prende in input un file audio e un prompt testuale e utilizza il modello
Qwen2-Audio per generare una risposta, salvando l'output in un file di testo.
"""

import argparse
import os
import logging
import torch
import time
from io import BytesIO
import librosa
import numpy as np
from transformers import Qwen2AudioForConditionalGeneration, AutoProcessor, GenerationConfig

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_audio_with_qwen(audio_file, text_prompt, output_file, model_id="Qwen/Qwen2-Audio-7B-Instruct"):
    """
    Processa un file audio e un prompt testuale usando il modello Qwen2-Audio

    Args:
        audio_file (str): Percorso del file audio
        text_prompt (str): Prompt testuale da inviare al modello
        output_file (str): Percorso dove salvare la risposta
        model_id (str): ID del modello Qwen da utilizzare
    """
    try:
        logger.info(f"Caricamento del modello {model_id}...")
        processor = AutoProcessor.from_pretrained(model_id)
        model = Qwen2AudioForConditionalGeneration.from_pretrained(model_id, device_map="auto")

        logger.info(f"Caricamento del file audio {audio_file}...")
        # Carica il file audio utilizzando librosa con sampling_rate esplicito
        target_sr = processor.feature_extractor.sampling_rate
        audio_data, sr = librosa.load(audio_file, sr=target_sr)

        logger.info(f"File audio caricato con sampling rate: {sr} Hz (target: {target_sr} Hz)")

        # Costruisci la conversazione in formato ChatML come richiesto da Qwen2-Audio
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": [
                {"type": "audio", "audio_url": audio_file},  # L'URL viene usato solo come riferimento
                {"type": "text", "text": text_prompt},
            ]},
        ]

        # Applica il template di chat
        logger.info("Preparazione dell'input per il modello...")
        text = processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)

        # Prepara l'input per il modello con sampling_rate esplicito
        inputs = processor(
            text=text,
            audio=[audio_data],  # Usa 'audio' invece di 'audios'
            sampling_rate=target_sr,
            return_tensors="pt",
            padding=True
        )

        # Sposta tutti gli input al device del modello
        device = model.device
        logger.info(f"Spostamento degli input sul device: {device}")
        for key, value in inputs.items():
            if hasattr(value, "to"):
                inputs[key] = value.to(device)

        # Crea una configurazione di generazione personalizzata che sovrascrive la predefinita
        generation_config = GenerationConfig(
            max_new_tokens=256,
            num_beams=5,          # Usiamo beam search con 5 beam per migliori risultati
            do_sample=False,      # No sampling
            temperature=None,     # Disattiva temperature
            top_p=None,           # Disattiva top_p
            top_k=None,           # Disattiva top_k
            early_stopping=True,  # Ha senso con num_beams > 1
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id
        )

        logger.info("Generazione della risposta...")
        logger.info("Questo potrebbe richiedere un po' di tempo, attendere prego...")

        # Usa solo gli input assolutamente necessari e la configurazione personalizzata
        start_time = time.time()

        with torch.no_grad():
            generate_ids = model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask if hasattr(inputs, "attention_mask") else None,
                generation_config=generation_config
            )

        generation_time = time.time() - start_time
        logger.info(f"Generazione completata in {generation_time:.2f} secondi")

        # Estrai solo i nuovi token generati (non quelli di input)
        new_tokens = generate_ids[:, inputs.input_ids.size(1):]

        # Decodifica la risposta
        response = processor.batch_decode(new_tokens, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

        # Salva la risposta nel file di output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response)

        logger.info(f"Risposta salvata in '{output_file}'")

        # Stampa anche la risposta nella console
        logger.info(f"Risposta del modello:\n{response}")

        return response

    except Exception as e:
        logger.error(f"Errore durante il processing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def main():
    parser = argparse.ArgumentParser(description='Test del modello Qwen2-Audio')
    parser.add_argument('-a', '--audio', type=str, required=True,
                        help='Percorso del file audio da processare')
    parser.add_argument('-p', '--prompt', type=str, required=True,
                        help='Prompt testuale da inviare al modello')
    parser.add_argument('-o', '--output', type=str, default='qwen_response.txt',
                        help='Nome del file di output (default: qwen_response.txt)')
    parser.add_argument('-m', '--model', type=str, default="Qwen/Qwen2-Audio-7B-Instruct",
                        help='ID del modello Qwen da utilizzare')

    args = parser.parse_args()

    # Verifica che il file audio esista
    if not os.path.exists(args.audio):
        logger.error(f"Il file audio '{args.audio}' non esiste")
        return

    try:
        process_audio_with_qwen(args.audio, args.prompt, args.output, args.model)
    except Exception as e:
        logger.error(f"Errore nell'esecuzione del test: {str(e)}")

if __name__ == '__main__':
    main()
