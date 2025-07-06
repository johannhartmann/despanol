import argparse
import os
import re
import sys
import time

import numpy as np
import pandas as pd
import pyphen
from appdirs import user_data_dir
from tensorflow.keras.models import load_model

import epitran

# --- Configuration ---
APP_NAME = "Despanol"
APP_AUTHOR = "Johann"
DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
DB_PATH = os.path.join(DATA_DIR, "spanish_database.csv")
MODEL_PATH = os.path.join(DATA_DIR, "s2s_model.keras")


def transliterate(
    german_text, model, input_token_index, target_token_index, max_decoder_seq_length
):
    """
    Transliterates a German text using the trained sequence-to-sequence model.
    """
    epi_de = epitran.Epitran("deu-Latn")
    german_ipa = epi_de.transliterate(german_text)

    encoder_input_data = np.zeros(
        (1, len(german_ipa), len(input_token_index)), dtype="float32"
    )
    for t, char in enumerate(german_ipa):
        if char in input_token_index:
            encoder_input_data[0, t, input_token_index[char]] = 1.0

    # Decode the input
    # This is a simplified decoding process. A more advanced implementation
    # would use a beam search here as well.
    target_seq = np.zeros((1, 1, len(target_token_index)))
    target_seq[0, 0, target_token_index["\t"]] = 1.0

    stop_condition = False
    decoded_sentence = ""
    while not stop_condition:
        output_tokens, h, c = model.layers[3].predict([target_seq] + states_value)

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = reverse_target_char_index[sampled_token_index]
        decoded_sentence += sampled_char

        if sampled_char == "\n" or len(decoded_sentence) > max_decoder_seq_length:
            stop_condition = True

        target_seq = np.zeros((1, 1, len(target_token_index)))
        target_seq[0, 0, sampled_token_index] = 1.0

        states_value = [h, c]

    return decoded_sentence


def main():
    """
    Main function to handle CLI arguments and the transliteration process.
    """
    parser = argparse.ArgumentParser(
        description="Phonetically transliterate a German text file to Spanish."
    )
    parser.add_argument(
        "input_file", help="Path to the input text file (use '-' for stdin)."
    )
    parser.add_argument(
        "--output", help="Path to the output text file (defaults to stdout)."
    )
    args = parser.parse_args()

    print("Loading model and database...", file=sys.stderr)
    start_time = time.time()
    try:
        model = load_model(MODEL_PATH)
        df = pd.read_csv(DB_PATH)
        df.dropna(subset=["ipa", "word"], inplace=True)

        input_texts = df["ipa"].tolist()
        target_texts = df["ipa"].tolist()
        input_characters = sorted(list(set("".join(input_texts))))
        target_characters = sorted(list(set("".join(target_texts))))
        max_decoder_seq_length = max([len(txt) for txt in target_texts])
        input_token_index = dict([(char, i) for i, char in enumerate(input_characters)])
        target_token_index = dict(
            [(char, i) for i, char in enumerate(target_characters)]
        )

    except FileNotFoundError:
        print(f"Error: Model or database not found.", file=sys.stderr)
        print(
            "Please run 'despanol-generate-data' and 'train.py' first.",
            file=sys.stderr,
        )
        sys.exit(1)

    end_time = time.time()
    print(f"Model and database ready in {end_time - start_time:.2f} seconds.\n", file=sys.stderr)

    if args.input_file == "-":
        lines = [line for line in sys.stdin.read().splitlines() if line]
    else:
        try:
            with open(args.input_file, "r") as f:
                lines = [line for line in f.read().splitlines() if line]
        except FileNotFoundError:
            print(f"Error: Input file not found at {args.input_file}", file=sys.stderr)
            sys.exit(1)

    output_lines = []
    for line in lines:
        spanish_output = transliterate(
            line, model, input_token_index, target_token_index, max_decoder_seq_length
        )
        output_lines.append(spanish_output)

    if args.output:
        try:
            with open(args.output, "w") as out_f:
                for line in output_lines:
                    out_f.write(line + "\n")
            print(
                f"\nTransliteration complete. Output saved to {args.output}",
                file=sys.stderr,
            )
        except IOError as e:
            print(f"Error writing to output file {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        for line in output_lines:
            print(line)


if __name__ == "__main__":
    main()