# tests/test_model.py
import os
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from tensorflow.keras.models import Model

from despanol.transliterate import transliterate


@pytest.fixture
def mock_model():
    """Creates a mock Keras model."""
    input1 = Model()
    with patch.object(input1.layers, "predict", return_value=(np.array([[[0.1]]]), 0, 0)):
        yield input1


def test_transliterate(mock_model):
    """
    Tests that the transliterate function returns a string.
    """
    input_token_index = {"a": 0, "\t": 1}
    target_token_index = {"b": 0, "\n": 1}
    max_decoder_seq_length = 5

    result = transliterate(
        "a", mock_model, input_token_index, target_token_index, max_decoder_seq_length
    )
    assert isinstance(result, str)

