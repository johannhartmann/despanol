import requests
import pandas as pd
import pyphen
import epitran
import os

def generate_database():
    """
    Downloads a Spanish word list, processes it to get IPA and syllable counts,
    and saves the results to a CSV file.
    """
    # URL of the Spanish word list from a GitHub repository
    url = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/es/es_50k.txt"
    
    # Download the word list
    print("Downloading Spanish word list...")
    response = requests.get(url)
    response.raise_for_status()
    print("Download complete.")
    
    # The content is a simple text file with one word per line, with frequency
    lines = response.text.splitlines()
    
    # Extract words from the lines
    words = [line.split(' ')[0] for line in lines]
            
    # Initialize pyphen for syllable counting and epitran for IPA conversion
    pyphen_dic = pyphen.Pyphen(lang='es_ES')
    epi = epitran.Epitran('spa-Latn')
    
    # Process each word
    data = []
    print(f"Processing {len(words)} words...")
    for i, word in enumerate(words):
        # Skip empty or NaN words
        if not word or pd.isna(word):
            continue
        
        try:
            # Generate IPA
            ipa = epi.transliterate(word)
            
            # Skip words that fail to transliterate to a non-empty string
            if not ipa:
                continue

            # Calculate syllable count
            syllables = len(pyphen_dic.inserted(word).split('-'))
            
            data.append({'word': word, 'ipa': ipa, 'syllables': syllables})
        except:
            # Skip words that fail to transliterate
            continue
        
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1} words...")
            
    print("Processing complete.")
    
    # Create a DataFrame and save to CSV
    df = pd.DataFrame(data)
    output_path = 'spanish_database.csv'
    df.to_csv(output_path, index=False)
    
    print(f"Database saved to {output_path}")

if __name__ == "__main__":
    generate_database()
