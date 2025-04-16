import os
import time
from pathlib import Path
import base64

# Importa la classe creata sopra
from eleven_labs_tts import ElevenLabsTTS

def test_eleven_labs():
    """Script di test per ElevenLabs TTS in italiano"""

    # Configurazione
    api_key = "sk_e4892f6b7081dad34cb0efc483e419d2f530cd10c634b40e" #os.environ.get("ELEVENLABS_API_KEY")  # Assicurati di impostare questa variabile d'ambiente
    output_dir = Path("./test_output")
    output_dir.mkdir(exist_ok=True)

    # Inizializza il client
    tts_client = ElevenLabsTTS(api_key, "XrExE9yKIg1WjnnlVkGX") #Matilda

    """
    Voci disponibili: 20
    Voce: Aria (ID: 9BWtsMINqrJLrRacOk9x)
    Voce: Roger (ID: CwhRBWXzGAHq8TQ4Fs17)
    Voce: Sarah (ID: EXAVITQu4vr4xnSDxMaL)
    Voce: Laura (ID: FGY2WhTYpPnrIDTdsKH5)
    Voce: Charlie (ID: IKne3meq5aSn9XLyUdCD)
    Voce: George (ID: JBFqnCBsd6RMkjVDRZzb)
    Voce: Callum (ID: N2lVS1w4EtoT3dr4eOWO)
    Voce: River (ID: SAz9YHcvj6GT2YYXdXww)
    Voce: Liam (ID: TX3LPaxmHKxFdv7VOQHJ)
    Voce: Charlotte (ID: XB0fDUnXU5powFXDhCwa)
    Voce: Alice (ID: Xb7hH8MSUJpSbSDYk0k2)
    Voce: Matilda (ID: XrExE9yKIg1WjnnlVkGX)
    Voce: Will (ID: bIHbv24MWmeRgasZH58o)
    Voce: Jessica (ID: cgSgspJ2msm6clMCkdW9)
    Voce: Eric (ID: cjVigY5qzO86Huf0OWal)
    Voce: Chris (ID: iP95p4xoKVk53GoZ742B)
    Voce: Brian (ID: nPczCjzI2devNBz1zQrb)
    Voce: Daniel (ID: onwK4e9ZLuTAKqWW03F9)
    Voce: Lily (ID: pFZP5JQG7iQjIQuC4Bku)
    Voce: Bill (ID: pqHfZKP75CvOlQylNhV4)
    """

    print("\nTest 2: Generare audio da testo in italiano")
    test_text = "Ciao, sono il tuo assistente personale con avatar 3D. Come posso aiutarti oggi?"
    output_path = output_dir / "test_italian.mp3"

    start_time = time.time()
    result = tts_client.convert_text_to_speech(test_text, output_path=output_path)
    end_time = time.time()

    if result:
        print(f"Audio generato con successo in {end_time-start_time:.2f} secondi!")
        print(f"File salvato in: {output_path}")
    else:
        print("Errore nella generazione dell'audio.")



    print("\nTest 4: Test con frasi più lunghe e varia punteggiatura")
    test_text_complex = """Buongiorno! Questo è un test del sistema di sintesi vocale per l'assistente personale.
    Sto testando frasi complesse, con punteggiatura varia: virgole, punti, esclamazioni!
    E anche domande? Funziona bene con l'italiano?"""

    output_path_complex = output_dir / "test_italian_complex.mp3"

    start_time = time.time()
    result_complex = tts_client.convert_text_to_speech(test_text_complex, output_path=output_path_complex)
    end_time = time.time()

    if result_complex:
        print(f"Audio complesso generato con successo in {end_time-start_time:.2f} secondi!")
        print(f"File salvato in: {output_path_complex}")
    else:
        print("Errore nella generazione dell'audio complesso.")

if __name__ == "__main__":
    test_eleven_labs()
