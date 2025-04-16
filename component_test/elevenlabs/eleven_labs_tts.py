import requests
import json
import os
from pathlib import Path

class ElevenLabsTTS:
    def __init__(self, api_key, voice_id=None, model_id="eleven_multilingual_v2"):
        """
        Inizializza il client ElevenLabs TTS.

        Args:
            api_key (str): La chiave API di ElevenLabs
            voice_id (str, optional): L'ID della voce da utilizzare
            model_id (str, optional): Il modello da utilizzare, default è eleven_multilingual_v2 per supporto multilingua
        """
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def list_voices(self):
        """Ottiene la lista delle voci disponibili"""
        url = f"{self.base_url}/voices"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Errore {response.status_code}: {response.text}")
            return None

    def convert_text_to_speech(self, text, output_path=None, voice_settings=None):
        """
        Converte il testo in audio utilizzando ElevenLabs.

        Args:
            text (str): Il testo da convertire in audio
            output_path (str, optional): Il percorso dove salvare il file audio
            voice_settings (dict, optional): Impostazioni della voce

        Returns:
            bytes or str: Dati audio o percorso del file salvato
        """
        if not self.voice_id:
            raise ValueError("Voice ID non specificato. Utilizzare list_voices() per trovare un ID voce.")

        url = f"{self.base_url}/text-to-speech/{self.voice_id}"

        # Impostazioni predefinite per la voce italiana
        default_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
            "speed": 1.0
        }

        # Utilizza le impostazioni personalizzate o quelle predefinite
        settings = voice_settings if voice_settings else default_settings

        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": settings
        }

        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code == 200:
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            else:
                return response.content
        else:
            print(f"Errore {response.status_code}: {response.text}")
            return None

    def convert_text_to_speech_with_timing(self, text, output_path=None, voice_settings=None):
        """
        Converte il testo in audio e ottiene i dati di timing per la sincronizzazione labiale.

        Args:
            text (str): Il testo da convertire in audio
            output_path (str, optional): Il percorso dove salvare il file audio
            voice_settings (dict, optional): Impostazioni della voce

        Returns:
            dict: Dati audio e timing
        """
        if not self.voice_id:
            raise ValueError("Voice ID non specificato. Utilizzare list_voices() per trovare un ID voce.")

        url = f"{self.base_url}/text-to-speech/{self.voice_id}/stream-with-timing"

        # Impostazioni predefinite per la voce italiana
        default_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
            "speed": 1.0
        }

        # Utilizza le impostazioni personalizzate o quelle predefinite
        settings = voice_settings if voice_settings else default_settings

        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": settings
        }

        response = requests.post(url, json=payload, headers=self.headers)

        if response.status_code == 200:
            response_data = response.json()

            # Estrai i dati audio e timing
            audio_data = response_data.get("audio_base64")
            alignment_data = response_data.get("alignment", {})

            result = {
                "audio_data": audio_data,
                "alignment": alignment_data
            }

            if output_path and audio_data:
                import base64
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(audio_data))

            return result
        else:
            print(f"Errore {response.status_code}: {response.text}")
            return None
