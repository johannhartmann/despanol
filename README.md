# Despanol: German to Spanish Phonetic Transliteration

A Python tool that transliterates German text into phonetically similar Spanish words while preserving the original syllable count.

## Description

This project provides a command-line tool to find Spanish words and phrases that phonetically mimic German text. The core goal is not translation, but **phonetic mimicry**.

The tool can be installed directly from GitHub and provides two command-line utilities:
*   `despanol-generate-data`: Downloads and prepares the necessary phonetic data.
*   `despanol`: The main transliteration tool.

## Installation

You can install the tool directly from GitHub using `pip`, `uv`, or `nix profile`.

### Using `pip`
```bash
pip install git+https://github.com/johannhartmann/despanol.git
```

### Using `uv`
```bash
uv pip install git+https://github.com/johannhartmann/despanol.git
```

### Using Nix
For a system-wide installation with Nix:
```bash
nix profile install github:johannhartmann/despanol
```

## Usage

### 1. Generate the Phonetic Database

Before you can perform any transliteration, you must first generate the Spanish phonetic database. This command only needs to be run once. It will download the necessary data and store it in a local user data directory.

```bash
despanol-generate-data
```
This will download a ~50,000-word Spanish frequency list and process it into a phonetic database, which takes a few minutes.

### 2. Train the Model

Once the database is generated, you must train the sequence-to-sequence model.

```bash
python train.py
```
This will train a simple sequence-to-sequence model with an attention mechanism on the phonetic database. The trained model will be saved to `s2s_model.keras` in the user's data directory.

### 3. Transliterate Text

Once the model is trained, you can use the `despanol` command to transliterate text.

**Command:**
```bash
despanol <input_file> --output <output_file>
```

**Arguments:**
*   `input_file`: The path to the input text file containing German text. Use `-` to read from standard input (stdin).
*   `--output`: (Optional) The path where the resulting Spanish transliteration will be saved. If omitted, the output will be printed to standard output (stdout).

**Examples:**

#### Transliterating a File:
1.  Create an input file `poem.txt`:
    ```
    Grüne Blätter, süßer Schall,
    Vögel zwitschern überall.
    ```

2.  Run the transliteration and save to a file:
    ```bash
    despanol poem.txt --output spanish_poem.txt
    ```
    The script will print its progress to the console and save the final result in `spanish_poem.txt`.

#### Using Pipes (stdin/stdout):
You can also use standard shell pipes to chain commands.

```bash
echo "Ich liebe dich" | despanol -
```

## Development

For development, you can use the included Nix Flake to get a reproducible environment with all dependencies.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/johannhartmann/despanol.git
    cd despanol
    ```

2.  **Enter the development shell:**
    ```bash
    nix develop
    ```
    You are now inside the project's environment with all tools and libraries available. The source code is in the `src/` directory.

## Quality Assurance

This project uses a suite of tools to ensure code quality.

### Formatting (Black)
To automatically format the code according to the project's style:
```bash
black src/ tests/
```

### Linting (Ruff)
To check for common errors and style issues:
```bash
ruff check src/ tests/
```

### Type Checking (MyPy)
To perform static type analysis:
```bash
mypy src/
```

### Testing (Pytest)
To run the test suite:
```bash
pytest
```