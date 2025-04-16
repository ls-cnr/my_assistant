# Assistente Personale con Avatar 3D Animato

Questo progetto implementa un assistente personale con avatar 3D animato che risponde alle richieste vocali degli utenti. Il sistema elabora l'input audio dell'utente, genera una risposta testuale, la converte in voce sintetizzata, e anima un avatar 3D con sincronizzazione labiale accurata per creare un'esperienza interattiva coinvolgente.

## Panoramica dell'Architettura

Il sistema è composto da quattro componenti principali organizzati in una pipeline sequenziale:

```
Audio input → [Qwen2-Audio] → Testo trascritto → [ElevenLabs] → Audio sintetizzato
                                    ↓
                        [Rhubarb Lip Sync] → Dati sincronizzazione labiale
                                    ↓
                        [Ready Player Me] → Avatar 3D animato con sincronizzazione labiale
```

## Requisiti di Sistema

- Python 3.8 o superiore
- FFmpeg
- Rhubarb Lip Sync
- Almeno 16GB di RAM (consigliati)
- GPU con almeno 8GB di VRAM (consigliata) per prestazioni ottimali

## Configurazione dell'Ambiente

### 1. Preparazione dell'Ambiente

#### Creazione della directory del progetto

```bash
mkdir avatar-3d-assistente
cd avatar-3d-assistente
```

#### Creazione dell'ambiente virtuale Python

```bash
# Per Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Per Windows
python -m venv venv
venv\Scripts\activate
```

#### Aggiornamento di pip

```bash
pip install --upgrade pip
```

### 2. Installazione delle Dipendenze

#### Installazione di FFmpeg

**Per macOS:**
```bash
brew install ffmpeg
```

**Per Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Per Windows:**
1. Scarica FFmpeg da [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Estrai i file in una directory (es. `C:\ffmpeg`)
3. Aggiungi la directory `bin` al PATH di sistema

#### Installazione di Rhubarb Lip Sync

1. Scarica l'ultima versione di Rhubarb Lip Sync dal [repository ufficiale](https://github.com/DanielSWolf/rhubarb-lip-sync/releases)
2. Crea una directory `bin` nel tuo progetto
3. Estrai il contenuto del file ZIP scaricato nella directory `bin`
4. Rendi l'eseguibile `rhubarb` eseguibile (su Linux/macOS):
   ```bash
   chmod +x bin/rhubarb
   ```

#### Installazione delle dipendenze Python

Crea un file `requirements.txt` con il seguente contenuto:

```
python-dotenv>=1.0.0
requests>=2.31.0
transformers>=4.35.0
torch>=2.0.0
numpy>=1.24.0
librosa>=0.10.0
soundfile>=0.12.0
pyaudio>=0.2.13
```

Installa le dipendenze:

```bash
pip install -r requirements.txt
```

### 3. Configurazione delle API

#### 3.1 Configurazione di Qwen2-Audio

Per utilizzare Qwen2-Audio, è necessario installare le dipendenze specifiche:

```bash
pip install git+https://github.com/huggingface/transformers
```

#### 3.2 Configurazione di ElevenLabs

1. Registrati su [ElevenLabs](https://elevenlabs.io/) per ottenere un'API key
2. Crea una voce o seleziona una voce esistente e annota il voice ID

### 4. Configurazione del Progetto

#### Creazione del file .env

Crea un file `.env` nella directory principale del progetto con il seguente contenuto:

```
# Credenziali ElevenLabs
ELEVEN_LABS_API_KEY=your_api_key_here
ELVEN_LABS_VOICE_ID=your_voice_id_here
ELEVEN_LABS_MODEL_ID=eleven_monolingual_v1

# Configurazioni Rhubarb
RHUBARB_PATH=./bin/rhubarb

# Percorso output
OUTPUT_DIR=./output
```

## Testare i Componenti

Organizza i test dei componenti in una struttura di directory come questa:

```
component_test/
├── elevenlabs/
│   ├── test_output/
│   ├── voice_list.py
│   └── test_eleven_labs.py
├── rhubarb/
│   ├── test_output/
│   ├── test_rhubarb.py
│   └── test_rhubarb_with_phonetic.py
└── qwen/
    ├── test_output/
    └── test_qwen.py
```

### Test di ElevenLabs

#### Ottenere la lista delle voci disponibili

```bash
python component_test/elevenlabs/voice_list.py
```

#### Testare la sintesi vocale

```bash
python component_test/elevenlabs/test_eleven_labs.py
```

### Test di Rhubarb Lip Sync

#### Test con il riconoscitore Phonetic (per lingue non inglesi)

```bash
python component_test/rhubarb/test_rhubarb_with_phonetic.py component_test/elevenlabs/test_output/test_italian_complex.mp3 --output component_test/rhubarb/test_output/output_phon.json
```

#### Test con il riconoscitore PocketSphinx (per lingua inglese)

```bash
python component_test/rhubarb/test_rhubarb.py component_test/elevenlabs/test_output/test_italian_complex.mp3 --output component_test/rhubarb/test_output/output_pock.json
```

### Test di Qwen2-Audio

```bash
python component_test/qwen/test_qwen.py -a input.mp3 -p "Qual è il contenuto di questo audio?" -o component_test/qwen/test_output/risposta.txt
```


## Risoluzione dei Problemi

### Problemi con ElevenLabs
- Verifica che la tua API key e Voice ID siano corretti nel file .env
- Assicurati di avere credito sufficiente sul tuo account ElevenLabs
- Controlla la connessione internet

### Problemi con Rhubarb Lip Sync
- Verifica che il percorso all'eseguibile sia corretto in .env
- Assicurati che l'eseguibile abbia i permessi di esecuzione
- Controlla che il formato audio sia supportato da Rhubarb

### Problemi con Qwen2-Audio
- Assicurati di avere abbastanza RAM e spazio GPU per il modello
- Verifica che il file audio sia in un formato supportato
- Per problemi di memoria, prova a usare versioni più piccole del modello
