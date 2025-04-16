import requests
import json
from prettytable import PrettyTable

def get_voice_list(api_key):
    """
    Ottiene e visualizza l'elenco delle voci disponibili da ElevenLabs con informazioni dettagliate.

    Args:
        api_key (str): La tua API key di ElevenLabs
    """
    url = "https://api.elevenlabs.io/v2/voices"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Crea una tabella per le voci
            table = PrettyTable()
            table.field_names = [
                "Voice ID",
                "Nome",
                "Categoria",
                "Accento",
                "Età",
                "Genere",
                "Caso d'uso",
                "Descrizione"
            ]

            # Imposta allineamento per rendere la tabella più leggibile
            table.align["Voice ID"] = "l"
            table.align["Nome"] = "l"
            table.align["Descrizione"] = "l"

            # Imposta la larghezza massima della colonna descrizione
            table.max_width["Descrizione"] = 40

            # Per ogni voce, estrai le informazioni pertinenti
            for voice in data['voices']:
                # Estrai voice_id e nome
                voice_id = voice.get('voice_id', 'N/A')
                name = voice.get('name', 'N/A')

                # Estrai categoria
                category = voice.get('category', 'N/A')

                # Estrai informazioni dalle etichette (labels)
                labels = voice.get('labels', {})
                accent = labels.get('accent', 'N/A')
                age = labels.get('age', 'N/A')
                gender = labels.get('gender', 'N/A')
                use_case = labels.get('use_case', 'N/A')

                # Estrai descrizione
                description = voice.get('description', 'N/A')
                if description and len(description) > 40:
                    description = description[:37] + "..."


                # Aggiungi una riga alla tabella
                table.add_row([
                    voice_id,
                    name,
                    category,
                    accent,
                    age,
                    gender,
                    use_case,
                    description
                ])

            # Stampa il numero totale di voci
            print(f"Numero totale di voci: {data.get('total_count', len(data['voices']))}")

            # Stampa la tabella
            print(table)

            # Ritorna i dati grezzi per eventuali elaborazioni successive
            return data

        else:
            print(f"Errore nella richiesta: {response.status_code}")
            print(f"Dettagli: {response.text}")
            return None

    except Exception as e:
        print(f"Si è verificato un errore: {e}")
        return None

if __name__ == "__main__":
    # Sostituisci con la tua API key
    api_key = "sk_e4892f6b7081dad34cb0efc483e419d2f530cd10c634b40e"

    # Per sicurezza, puoi caricare l'API key da un file o variabile d'ambiente
    # import os
    # api_key = os.environ.get("ELEVENLABS_API_KEY")

    # Se preferisci caricare da un file
    # with open('.api_key', 'r') as f:
    #     api_key = f.read().strip()

    get_voice_list(api_key)
