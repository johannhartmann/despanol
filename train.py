import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Attention

def train_model():
    """
    Trains a sequence-to-sequence model with attention to transliterate
    German IPA to Spanish IPA.
    """
    # Load the Spanish database
    try:
        df = pd.read_csv('spanish_database.csv')
        df.dropna(subset=['ipa', 'word'], inplace=True)
    except FileNotFoundError:
        print("Error: spanish_database.csv not found.")
        print("Please run generate_data.py first to create the database.")
        return

    # For this simple example, we will use the Spanish data as both the
    # source and target, to learn the phonetics of the language.
    # A more advanced model would use a parallel corpus of German and Spanish.
    input_texts = df['ipa'].tolist()
    target_texts = df['ipa'].tolist()

    input_characters = sorted(list(set("".join(input_texts))))
    target_characters = sorted(list(set("".join(target_texts))))
    num_encoder_tokens = len(input_characters)
    num_decoder_tokens = len(target_characters)
    max_encoder_seq_length = max([len(txt) for txt in input_texts])
    max_decoder_seq_length = max([len(txt) for txt in target_texts])

    input_token_index = dict([(char, i) for i, char in enumerate(input_characters)])
    target_token_index = dict([(char, i) for i, char in enumerate(target_characters)])

    encoder_input_data = np.zeros(
        (len(input_texts), max_encoder_seq_length, num_encoder_tokens), dtype="float32"
    )
    decoder_input_data = np.zeros(
        (len(input_texts), max_decoder_seq_length, num_decoder_tokens), dtype="float32"
    )
    decoder_target_data = np.zeros(
        (len(input_texts), max_decoder_seq_length, num_decoder_tokens), dtype="float32"
    )

    for i, (input_text, target_text) in enumerate(zip(input_texts, target_texts)):
        for t, char in enumerate(input_text):
            encoder_input_data[i, t, input_token_index[char]] = 1.0
        for t, char in enumerate(target_text):
            decoder_input_data[i, t, target_token_index[char]] = 1.0
            if t > 0:
                decoder_target_data[i, t - 1, target_token_index[char]] = 1.0

    # Build the model
    encoder_inputs = Input(shape=(None, num_encoder_tokens))
    encoder = LSTM(256, return_sequences=True, return_state=True)
    encoder_outputs, state_h, state_c = encoder(encoder_inputs)
    encoder_states = [state_h, state_c]

    decoder_inputs = Input(shape=(None, num_decoder_tokens))
    decoder_lstm = LSTM(256, return_sequences=True, return_state=True)
    decoder_outputs, _, _ = decoder_lstm(decoder_inputs, initial_state=encoder_states)
    
    attention = Attention()([decoder_outputs, encoder_outputs])
    
    decoder_dense = Dense(num_decoder_tokens, activation="softmax")
    decoder_outputs = decoder_dense(attention)

    model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

    model.compile(
        optimizer="rmsprop", loss="categorical_crossentropy", metrics=["accuracy"]
    )
    model.fit(
        [encoder_input_data, decoder_input_data],
        decoder_target_data,
        batch_size=64,
        epochs=10,
        validation_split=0.2,
    )

    # Save the model
    model.save("s2s_model.keras")

if __name__ == "__main__":
    train_model()
