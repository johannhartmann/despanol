# tests/conftest.py
import pytest
import pandas as pd
import pyphen
import epitran
import os

@pytest.fixture(scope="session")
def mock_db_path():
    """Returns the path to the mock database."""
    return os.path.join(os.path.dirname(__file__), "mock_spanish_database.csv")

@pytest.fixture(scope="session")
def spanish_words_by_syllable(mock_db_path):
    """Loads and processes the mock Spanish database into a dictionary."""
    df = pd.read_csv(mock_db_path)
    df.dropna(subset=['ipa', 'word'], inplace=True)
    
    word_dict = {}
    for _, row in df.iterrows():
        syllables = int(row['syllables'])
        if syllables not in word_dict:
            word_dict[syllables] = []
        word_dict[syllables].append({'word': row['word'], 'ipa': row['ipa']})
    return word_dict

@pytest.fixture(scope="session")
def pyphen_dic_de():
    """Provides a Pyphen dictionary for German."""
    return pyphen.Pyphen(lang='de_DE')

@pytest.fixture(scope="session")
def epi_de():
    """Provides an Epitran instance for German."""
    return epitran.Epitran('deu-Latn')
