# Despanol: German to Spanish Phonetic Transliteration

A Python tool that transliterates German text into phonetically similar Spanish words while preserving the original syllable count.

## Description

This project provides a command-line tool to find Spanish words and phrases that phonetically mimic German text. The core goal is not translation, but **phonetic mimicry**. The tool is built using a reproducible development environment defined by Nix Flakes.

The process involves:
1.  A data generation script (`generate_data.py`) that builds a phonetic database of over 49,000 Spanish words, including their IPA pronunciation and syllable count.
2.  The main transliteration script (`transliterate.py`) which uses a beam search algorithm to find the best phonetic match for a given German text from the database. It prioritizes finding a perfect syllable match and includes a fallback to find the closest possible match if a perfect one isn't available.

## Installation & Environment Setup

The entire project is managed by [Nix Flakes](https://nixos.wiki/wiki/Flakes), ensuring a fully reproducible development environment.

### Prerequisites

You must have Nix installed with Flakes enabled. You can follow the instructions on the [official Nix website](https://nixos.org/download.html).

### Running the Environment

1.  **Clone the repository:**
    ```bash
    git clone <repo_url>
    cd despanol
    ```

2.  **Enter the development shell:**
    Running the following command will automatically download all required dependencies (Python, libraries, etc.) and drop you into a shell where everything is ready to use.

    ```bash
    nix develop
    ```

    You are now inside the project's environment.

## Usage

The project is split into two main scripts.

### 1. Generate the Phonetic Database

Before you can perform any transliteration, you must first generate the Spanish phonetic database.

Inside the `nix develop` shell, run:
```bash
python generate_data.py
```
This will download a Spanish word frequency list and create the `spanish_database.csv` file in the project root. This only needs to be done once.

### 2. Transliterate a File

The main tool provides a command-line interface for transliterating a German text file.

**Command:**
```bash
python transliterate.py --input <input_file.txt> --output <output_file.txt>
```

**Arguments:**
*   `--input`: The path to the input text file containing German text.
*   `--output`: The path where the resulting Spanish transliteration will be saved.

**Example:**

1.  Create an input file `poem.txt`:
    ```
    Grüne Blätter, süßer Schall,
    Vögel zwitschern überall.
    ```

2.  Run the transliteration:
    ```bash
    python transliterate.py --input poem.txt --output spanish_poem.txt
    ```

3.  The script will print its progress to the console and save the final result in `spanish_poem.txt`.

    **Console Output:**
    ```
    [1/2] Processing line...
      German:  Grüne Blätter, süßer Schall,
      Spanish: camino platt personal
      (Took 25.51s, ETA: 32.78s)

    [2/2] Processing line...
      German:  Vögel zwitschern überall.
      Spanish: fue el chist carnaval
      (Took 32.78s, ETA: 0.00s)

    Transliteration complete. Output saved to spanish_poem.txt
    ```

    **`spanish_poem.txt` Contents:**
    ```
    camino platt personal
    fue el chist carnaval
    ```
