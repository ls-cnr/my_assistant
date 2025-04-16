#!/bin/bash
# Script di installazione per configurare l'ambiente di sviluppo per il progetto di avatar 3D animato
# Specifico per macOS

set -e  # Interrompe l'esecuzione in caso di errore

# Colori per i messaggi
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per stampare messaggi informativi
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Funzione per stampare messaggi di successo
success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Funzione per stampare messaggi di errore
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Funzione per stampare messaggi di avviso
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verifica se Homebrew è installato
check_homebrew() {
    info "Verificando se Homebrew è installato..."
    if ! command -v brew &> /dev/null; then
        warning "Homebrew non è installato. Procedo con l'installazione..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        success "Homebrew installato con successo"
    else
        success "Homebrew è già installato"
    fi
}

# Installa ffmpeg
install_ffmpeg() {
    info "Verificando se ffmpeg è installato..."
    if ! command -v ffmpeg &> /dev/null; then
        info "Installando ffmpeg..."
        brew install ffmpeg
        success "ffmpeg installato con successo"
    else
        success "ffmpeg è già installato"
    fi
}

# Scarica e installa Rhubarb Lip Sync
install_rhubarb() {
    info "Scaricando e installando Rhubarb Lip Sync..."

    # Crea directory bin se non esiste
    mkdir -p bin

    # Determina la versione più recente di Rhubarb
    RHUBARB_VERSION="1.13.0"

    # Determina il sistema (macOS)
    RHUBARB_ZIP="rhubarb-lip-sync-${RHUBARB_VERSION}-macOS.zip"
    RHUBARB_URL="https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v${RHUBARB_VERSION}/${RHUBARB_ZIP}"

    # Scarica Rhubarb
    info "Scaricando Rhubarb da ${RHUBARB_URL}..."
    curl -L -o "${RHUBARB_ZIP}" "${RHUBARB_URL}"

    # Estrai nella directory bin
    info "Estraendo Rhubarb nella directory bin..."
    unzip -o "${RHUBARB_ZIP}" -d bin/

    # Rendi l'eseguibile Rhubarb eseguibile
    chmod +x bin/rhubarb

    # Rimuovi lo zip scaricato
    rm "${RHUBARB_ZIP}"

    success "Rhubarb Lip Sync installato con successo in ./bin/"
}

# Configura l'ambiente Python
setup_python_env() {
    info "Configurando l'ambiente Python..."

    # Verifica se Python è installato
    if ! command -v python3 &> /dev/null; then
        warning "Python 3 non trovato. Lo installo con Homebrew..."
        brew install python
    else
        success "Python 3 è già installato"
    fi

    # Crea e attiva l'ambiente virtuale
    info "Creando l'ambiente virtuale Python..."
    python3 -m venv venv

    # Aggiorna pip
    info "Aggiornando pip all'ultima versione..."
    source venv/bin/activate
    pip install --upgrade pip

    # Installa le dipendenze Python
    info "Installando le dipendenze Python..."
    pip install python-dotenv requests

    success "Ambiente Python configurato con successo"
}

# Crea un file .env di esempio
create_env_file() {
    info "Creando un file .env di esempio..."
    if [ ! -f .env ]; then
        cat > .env << EOL
# Credenziali ElevenLabs
ELEVEN_LABS_API_KEY=your_api_key_here
ELVEN_LABS_VOICE_ID=your_voice_id_here
ELEVEN_LABS_MODEL_ID=eleven_monolingual_v1

# Configurazioni Rhubarb
RHUBARB_PATH=./bin/rhubarb
EOL
        success "File .env di esempio creato. RICORDATI DI MODIFICARLO CON LE TUE CREDENZIALI!"
    else
        warning "Il file .env già esiste. Non è stato sovrascritto."
    fi
}

# Funzione principale
main() {
    echo "====================================================================="
    echo "  SETUP AMBIENTE PER PROGETTO AVATAR 3D CON SINCRONIZZAZIONE LABIALE"
    echo "====================================================================="

    # Verifica e installa le dipendenze necessarie
    check_homebrew
    install_ffmpeg
    install_rhubarb
    setup_python_env
    create_env_file

    echo "====================================================================="
    echo "  INSTALLAZIONE COMPLETATA"
    echo "====================================================================="
    echo ""
    info "Per attivare l'ambiente virtuale, esegui: source venv/bin/activate"
    info "Modifica il file .env con le tue credenziali ElevenLabs"
    info "Per testare Rhubarb con audio in italiano:"
    echo "  python test_rhubarb_with_phonetic.py percorso/al/file/audio.mp3"
    echo ""
    success "Ambiente configurato con successo!"
}

# Esegui la funzione principale
main
