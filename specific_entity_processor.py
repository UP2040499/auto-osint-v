"""
This module will identify specific entities in the intelligence statement and 
store them in appropriate stores.
Subprocesses to this module attempt to interrogate some of this information.
"""

# Requires Named Entity Recognition (NER) using NLP

import spacy

NER = spacy.load("en_core_web_sm")
class EntityProcessor():
    def __init__(self, intel_statement):
        self.intel_statement = intel_statement

    def test_func(self):
        text1= NER(self.intel_statement)

        for word in text1.ents:
            print(word.text,word.label_)    # prints the entity and its label. e.g., "MARS LOC"
            
