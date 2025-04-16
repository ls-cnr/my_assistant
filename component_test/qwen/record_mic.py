#!/usr/bin/env python3
"""
Script per registrare audio dal microfono e salvarlo come file MP3.
Supporta la registrazione con durata specificata o fino all'interruzione manuale.
"""

import argparse
import os
import time
import wave
import tempfile
import pyaudio
import pydub

def record_audio(output_file, duration=None, sample_rate=44100, channels=1, chunk=1024):
    """
    Registra audio dal microfono e lo salva come file MP3.

    Args:
        output_file (str): Percorso del file di output (MP3)
        duration (int, optional): Durata della registrazione in secondi. None per registrare fino a CTRL+C.
        sample_rate (int): Frequenza di campionamento
        channels (int): Numero di canali (1=mono, 2=stereo)
        chunk (int): Dimensione del chunk audio
    """
    p = pyaudio.PyAudio()

    # Formato di registrazione: 16 bit PCM
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("Registrazione in corso...")
    frames = []

    try:
        # Registrazione a tempo determinato o indeterminato
        if duration:
            for i in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
                # Mostra progresso
                if i % int(sample_rate / chunk) == 0:
                    seconds = i // int(sample_rate / chunk)
                    print(f"Registrati {seconds} secondi di {duration}...")
        else:
            print("Premi CTRL+C per interrompere la registrazione")
            while True:
                data = stream.read(chunk)
                frames.append(data)
    except KeyboardInterrupt:
        print("\nRegistrazione interrotta dall'utente")
    finally:
        # Ferma e chiudi lo stream
        stream.stop_stream()
        stream.close()
        p.terminate()

    print("Registrazione completata!")

    # Salva prima come WAV temporaneo, poi converti in MP3
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
        temp_wav_path = temp_wav.name

    wf = wave.open(temp_wav_path, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Conversione in MP3
    sound = pydub.AudioSegment.from_wav(temp_wav_path)
    sound.export(output_file, format="mp3")

    # Rimuovi il file WAV temporaneo
    os.unlink(temp_wav_path)

    print(f"Audio salvato come '{output_file}'")

def main():
    parser = argparse.ArgumentParser(description='Registra audio dal microfono in formato MP3')
    parser.add_argument('-o', '--output', type=str, default='recording.mp3',
                        help='Nome del file di output (default: recording.mp3)')
    parser.add_argument('-d', '--duration', type=int,
                        help='Durata della registrazione in secondi (se non specificato, registra fino a CTRL+C)')
    parser.add_argument('-r', '--rate', type=int, default=44100,
                        help='Frequenza di campionamento (default: 44100 Hz)')
    parser.add_argument('-c', '--channels', type=int, default=1,
                        help='Numero di canali (1=mono, 2=stereo, default: 1)')

    args = parser.parse_args()

    record_audio(args.output, args.duration, args.rate, args.channels)

if __name__ == '__main__':
    main()
