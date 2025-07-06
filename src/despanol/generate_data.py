import pandas as pd
import pyphen
import epitran
import os
import requests
from appdirs import user_data_dir

# --- Configuration ---
APP_NAME = "Despanol"
APP_AUTHOR = "Johann"
DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
DB_PATH = os.path.join(DATA_DIR, "spanish_database.csv")

def generate_database():
    """
    Downloads a Spanish word list, processes it to get IPA and syllable counts,
    and saves the results to a CSV file in the user's data directory.
    """
    print(f"Database will be saved to: {DB_PATH}")
    os.makedirs(DATA_DIR, exist_ok=True)

    # URL of the Spanish word list from a GitHub repository
    url = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/es/es_50k.txt"
    
    print("Downloading Spanish word list...")
    response = requests.get(url)
    response.raise_for_status()
    print("Download complete.")
    
    lines = response.text.splitlines()
    words = [line.split(' ')[0] for line in lines]
            
    pyphen_dic = pyphen.Pyphen(lang='es_ES')
    epi = epitran.Epitran('spa-Latn')
    
    data = []
    total_words = len(words)
    print(f"Processing {total_words} words...")
    for i, word in enumerate(words):
        if not word or pd.isna(word):
            continue
        
        try:
            ipa = epi.transliterate(word)
            if not ipa:
                continue
            syllables = len(pyphen_dic.inserted(word).split('-'))
            data.append({'word': word, 'ipa': ipa, 'syllables': syllables})
        except Exception:
            continue
        
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{total_words} words...")
            
    print("Processing complete.")
    
    df = pd.DataFrame(data)
    df.to_csv(DB_PATH, index=False)
    
    print(f"Database successfully saved to {DB_PATH}")

def main():
    """
    Main function to be called by the entry point script.
    """
    try:
        generate_database()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()