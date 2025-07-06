import argparse
import os
import re
import sys
import time

import epitran
import Levenshtein
import pandas as pd
import pyphen
from appdirs import user_data_dir

# --- Configuration ---
BEAM_WIDTH = 50
MAX_CHUNK_SIZE = 4
APP_NAME = "Despanol"
APP_AUTHOR = "Johann"
DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
DB_PATH = os.path.join(DATA_DIR, "spanish_database.csv")


def transliterate(german_text, spanish_words_by_syllable, pyphen_dic_de, epi_de):
    """
    Transliterates a German text using an optimized beam search algorithm.
    """
    german_words = re.findall(r"\b\w+\b", german_text.lower())
    german_syllables_ipa = []
    for word in german_words:
        syllables = pyphen_dic_de.inserted(word).split("-")
        for syllable in syllables:
            german_syllables_ipa.append(epi_de.transliterate(syllable))

    target_syllable_count = len(german_syllables_ipa)
    if target_syllable_count == 0:
        return ""

    initial_hypothesis = (0, [], 0)
    beam = [initial_hypothesis]

    while True:
        new_hypotheses = []
        all_done = all(h[2] >= target_syllable_count for h in beam)
        if all_done:
            break

        for score, path, index in beam:
            if index >= target_syllable_count:
                new_hypotheses.append((score, path, index))
                continue

            for chunk_len in range(1, MAX_CHUNK_SIZE + 1):
                if index + chunk_len > target_syllable_count:
                    continue

                german_chunk_ipa = "".join(
                    german_syllables_ipa[index : index + chunk_len]
                )
                candidate_words = spanish_words_by_syllable.get(chunk_len, [])

                for candidate in candidate_words:
                    distance = Levenshtein.distance(german_chunk_ipa, candidate["ipa"])
                    new_path = path + [candidate["word"]]
                    new_score = score + distance
                    new_index = index + chunk_len
                    new_hypotheses.append((new_score, new_path, new_index))

        if not new_hypotheses:
            break
        new_hypotheses.sort(key=lambda x: x[0] / x[2] if x[2] > 0 else 0)
        beam = new_hypotheses[:BEAM_WIDTH]

    best_hypothesis = None
    lowest_score = float("inf")

    perfect_matches = [h for h in beam if h[2] == target_syllable_count]
    if perfect_matches:
        perfect_matches.sort(key=lambda x: x[0])
        return " ".join(perfect_matches[0][1])

    for score, path, final_count in beam:
        if abs(final_count - target_syllable_count) == 0:
            normalized_score = score / final_count if final_count > 0 else 0
            if normalized_score < lowest_score:
                lowest_score = normalized_score
                best_hypothesis = path

    if best_hypothesis:
        return " ".join(best_hypothesis)
    else:
        return "<?> (No translation could be generated)"


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

    print("Loading and pre-processing database...", file=sys.stderr)
    start_time = time.time()
    try:
        df = pd.read_csv(DB_PATH)
        df.dropna(subset=["ipa", "word"], inplace=True)

        spanish_words_by_syllable = {}
        for _, row in df.iterrows():
            syllables = int(row["syllables"])
            if syllables not in spanish_words_by_syllable:
                spanish_words_by_syllable[syllables] = []
            spanish_words_by_syllable[syllables].append(
                {"word": row["word"], "ipa": row["ipa"]}
            )

    except FileNotFoundError:
        print(f"Error: Database not found at {DB_PATH}", file=sys.stderr)
        print(
            "Please run 'despanol-generate-data' first to create it.", file=sys.stderr
        )
        sys.exit(1)

    pyphen_dic_de = pyphen.Pyphen(lang="de_DE")
    epi_de = epitran.Epitran("deu-Latn")

    end_time = time.time()
    print(f"Database ready in {end_time - start_time:.2f} seconds.\n", file=sys.stderr)

    if args.input_file == "-":
        lines = [line for line in sys.stdin.read().splitlines() if line]
    else:
        try:
            with open(args.input_file, "r") as f:
                lines = [line for line in f.read().splitlines() if line]
        except FileNotFoundError:
            print(f"Error: Input file not found at {args.input_file}", file=sys.stderr)
            sys.exit(1)

    total_lines = len(lines)
    processing_times = []

    output_lines = []
    for i, line in enumerate(lines):
        line_start_time = time.time()

        spanish_output = transliterate(
            line, spanish_words_by_syllable, pyphen_dic_de, epi_de
        )
        output_lines.append(spanish_output)

        line_end_time = time.time()
        line_duration = line_end_time - line_start_time
        processing_times.append(line_duration)

        avg_time = sum(processing_times) / len(processing_times)
        lines_remaining = total_lines - (i + 1)
        eta = avg_time * lines_remaining

        print(
            f"[{i+1}/{total_lines}] Processed line in {line_duration:.2f}s. "
            f"ETA: {eta:.2f}s",
            file=sys.stderr,
        )

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
