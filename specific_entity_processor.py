"""
This module will identify specific entities in the intelligence statement and 
store them in appropriate stores.
Subprocesses to this module attempt to interrogate some of this information.
"""

# Named Entity Recognition (NER) using NLP

import spacy

# Load the best model trained using Google Colab
NER = spacy.load("NER_training_testing/train/model/model-best-from-colab")


class EntityProcessor:
    """
    This class provides methods for recognising the individual entities in a statement and storing them appropriately.
    """
    def __init__(self, intel_statement, file_handler):
        """
        Initialises variables to be used in this object.
        :param intel_statement: This is the intelligence statement input in main.py
        """
        self.intel_statement = intel_statement
        self.file_handler = file_handler

    def store_words_from_label(self):
        """
        This function stores recognised words in csv files that are relevant to the label given to the word.
        :return: Nothing - stores info in files
        """
        # Clean any leftover files from previous runs
        self.file_handler.clean_directory("data_files/target_info_files")
        text1 = NER(self.intel_statement)
        for word in text1.ents:
            # store word in appropriate .csv file based on label
            print(word.text, "LABEL: ", word.label_)    # prints the entity and its label. e.g., "MARS LOC"
            # Open the relevant (based on word label) csv file and store the word text
            self.file_handler.open_label_file(word.label_, word.text, alias="")
