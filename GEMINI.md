# Gemini Project: despanol

This project, "despanol," is a Python-based tool for phonetic transliteration from German to Spanish. It is designed to find Spanish words that phonetically mimic German text, maintaining the same syllable count.

## Tool: despanol

The `despanol` tool is the primary interface for this project.

### Usage

To use the tool, you will provide a German text string as input. The tool will then process this input and return a phonetically similar Spanish string.

**Example:**

*   **German Input:** "Ich liebe dich"
*   **Spanish Output:** "y libre di"

### How it Works

The tool operates in two main stages:

1.  **Data Generation:** A script (`generate_data.py`) builds a phonetic database of Spanish words. This involves:
    *   Processing a comprehensive list of Spanish words.
    *   Generating an IPA (International Phonetic Alphabet) string for each word.
    *   Calculating the syllable count for each word.
    *   Storing this information in a `spanish_database.csv` file.

2.  **Transliteration:** The main tool (`transliterate.py`) uses the generated database to perform the transliteration. This involves:
    *   Analyzing the German input string to determine its IPA syllables.
    *   Searching the Spanish database for words or sequences of words that phonetically match the German syllables.
    *   Using a phonetic similarity algorithm to find the best-matching Spanish words.
    *   Assembling the resulting Spanish words into the final output string.

### Development Environment

The entire project is built within a reproducible development environment defined by Nix Flakes and `uv`. This ensures that all dependencies and configurations are consistent. The `flake.nix` file sets up the environment, and `uv` is used for Python package management.
