"""
This module will identify specific entities in the intelligence statement and 
store them in appropriate stores.
Subprocesses to this module attempt to interrogate some of this information.
"""

# Requires Named Entity Recognition (NER) using NLP

import spacy

# Load the best model trained using Google Colab
NER = spacy.load("NER_training_testing/train/model/model-best-from-colab")


class EntityProcessor:
    """
    This class provides methods for recognising the individual entities in a statement and storing them appropriately.
    """
    def __init__(self, intel_statement):
        self.intel_statement = intel_statement

    def test_func(self):
        text1 = NER(self.intel_statement)

        for word in text1.ents:
            print(word.text, "LABEL: ", word.label_)    # prints the entity and its label. e.g., "MARS LOC"
            
