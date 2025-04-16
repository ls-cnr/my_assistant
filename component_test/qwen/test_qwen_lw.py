#!/usr/bin/env python3
"""
Script per testare il modello Qwen2-Audio con impostazioni ottimizzate per sistemi con risorse limitate.
"""

import argparse
import os
import logging
import torch
import gc
from transformers import Qwen2AudioForConditionalGeneration, AutoProcessor, GenerationConfig

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def free_memory():
    """Libera la memoria non utilizzata"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

def process_audio_with_qwen(audio_file, text_prompt, output_file, model_id="Qwen/Qwen2-Audio-7B-Instruct"):
    """
    Processa un file audio e un prompt testuale usando il modello Qwen2-Audio
    con impostazioni ottimizzate per risorse limitate.
    """
    try:
        # Libera memoria prima di iniziare
        free_memory()

        # Imposta opzioni di caricamento per ridurre l'uso di memoria
        logger.info(f"Caricamento del modello {model_id} in modalità a basso consumo di memoria...")

        # Carica il processor normalmente
        processor = AutoProcessor.from_pretrained(model_id)

        # Carica il modello con ottimizzazioni di memoria
        model_loading_kwargs = {
            "device_map": "auto",  # Auto-distribuzione su dispositivi disponibili
            "torch_dtype": torch.float16,  # Usa precisione ridotta (half-precision)
            "offload_folder": "offload",  # Cartella per offload dei tensori
            "offload_state_dict": True,  # Abilita offload dello state dict
            "low_cpu_mem_usage": True     # Riduce uso di memoria CPU
        }

        model = Qwen2AudioForConditionalGeneration.from_pretrained(
            model_id,
            **model_loading_kwargs
        )

        # Dopo aver caricato il modello, esegui pulizia della memoria
        free_memory()

        logger.info(f"Caricamento del file audio {audio_file}...")
        import librosa

        # Carica l'audio con un sample rate ridotto per risparmiare memoria
        target_sr = processor.feature_extractor.sampling_rate
        audio_data, sr = librosa.load(audio_file, sr=target_sr, mono=True)

        logger.info(f"Audio caricato: durata={len(audio_data)/sr:.2f}s, sr={sr}Hz")

        # Costruisci la conversazione più semplice possibile per ridurre dimensioni
        conversation = [
            {"role": "user", "content": [
                {"type": "audio", "audio_url": audio_file},
                {"type": "text", "text": text_prompt},
            ]},
        ]

        # Applica il template di chat
        logger.info("Preparazione dell'input per il modello...")
        text = processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)

        # Prepara l'input usando 'audio' invece di 'audios'
        inputs = processor(
            text=text,
            audio=[audio_data],
            sampling_rate=target_sr,
            return_tensors="pt",
            padding=True
        )

        # Sposta input sul device del modello (potrebbero essere diversi a causa di device_map)
        logger.info(f"Device del modello: {model.device}")
        for key, value in inputs.items():
            if hasattr(value, "to"):
                inputs[key] = value.to(model.device)

        # Crea una configurazione di generazione estremamente semplice e leggera
        generation_config = GenerationConfig(
            max_new_tokens=128,      # Riduci la lunghezza massima dell'output
            num_beams=1,             # Nessun beam search per risparmiare memoria
            do_sample=False,         # Generazione deterministica
            temperature=None,        # Disattiva temperature
            top_p=None,              # Disattiva top_p
            top_k=None,              # Disattiva top_k
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id
        )

        logger.info("Avvio della generazione...")
        logger.info("Questo potrebbe richiedere del tempo, attendere prego...")

        # Libera memoria prima della generazione
        free_memory()

        # Esegui la generazione con torch.no_grad() per risparmiare memoria
        with torch.no_grad():
            generate_ids = model.generate(
                input_ids=inputs.input_ids,
                generation_config=generation_config
            )

        # Estrai solo i nuovi token generati
        new_tokens = generate_ids[:, inputs.input_ids.size(1):]

        # Decodifica la risposta
        response = processor.batch_decode(new_tokens, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

        # Libera memoria dopo la generazione
        free_memory()

        # Salva la risposta nel file di output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response)

        logger.info(f"Risposta salvata in '{output_file}'")
        logger.info(f"Risposta del modello:\n{response}")

        return response

    except Exception as e:
        logger.error(f"Errore durante il processing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def main():
    parser = argparse.ArgumentParser(description='Test del modello Qwen2-Audio ottimizzato per risorse limitate')
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
        # Imposta variabili d'ambiente per ottimizzare l'uso della memoria
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"

        process_audio_with_qwen(args.audio, args.prompt, args.output, args.model)
    except Exception as e:
        logger.error(f"Errore nell'esecuzione del test: {str(e)}")

if __name__ == '__main__':
    main()
