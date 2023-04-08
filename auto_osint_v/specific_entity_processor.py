"""This module will identify specific entities

These entities are extracted from the intelligence statement and
stored in appropriate stores.
Subprocesses to this module attempt to interrogate some of this information.
"""

import spacy


# Load the best model trained using Google Colab
NER = spacy.load("auto_osint_v/NER_training_testing/train/model/model-best-from-colab")


class EntityProcessor:
    """This class extracts the entities from a given statement

    It provides methods for recognising the individual entities in a statement and storing
    them appropriately.
    """
    def __init__(self, read_statement, file_handler_object):
        """Initialises variables to be used in this object.

        Args:
         read_statement: the statement read from a text file
        """
        self.statement = read_statement
        self.file_handler = file_handler_object

    def store_words_from_label(self):
        """This function stores recognised words in csv files

        These files are associated with the label given to
        the word.

        Returns
         Nothing - stores info in files
        """
        # Clean any leftover files from previous runs
        self.file_handler.clean_directory("data_files/target_info_files")
        text1 = NER(self.statement)

        # changes added to eliminate duplicates and count number of mentions
        # define list of words present
        words_present = {}

        for word in text1.ents:
            # prints the entity and its label. e.g., "MARS LOC"
            # print(word.text, "LABEL: ", word.label_)
            # append the word to the list of words
            key = word.text
            # see python EAFP
            try:
                words_present[key][1] += 1
            except KeyError:
                words_present[key] = [word.label_, 1]

        for text, [label, mentions] in words_present.items():
            # Opens the relevant (based on word label) csv file and store the word text
            # and number of mentions.
            self.file_handler.open_label_file(label, text, mentions=mentions)
