"""This module will identify specific entities

These entities are extracted from the intelligence statement and
stored in appropriate stores.
Subprocesses to this module attempt to interrogate some of this information.
"""
import os
import spacy

# Load the best model trained using Google Colab
try:
    NER = spacy.load(os.getcwd() + "/NER_training_testing/train/model/model-best-from-colab")
except OSError:
    os.chdir("../auto_osint_v/")
    NER = spacy.load("NER_training_testing/train/model/model-best-from-colab")
NER.add_pipe('sentencizer')


class EntityProcessor:
    """This class extracts the entities from a given statement

    It provides methods for recognising the individual entities in a statement and storing
    them appropriately.
    """
    def __init__(self, file_handler_object):
        """Initialises variables to be used in this object.

        Args:
         file_handler_object: the file handler to be used for file IO operations
        """
        self.file_handler = file_handler_object
        self.irrelevant_words = ["it", "them", "they", "the", "he", "she", "his", "her", "we", "i",
                                 "us", "me", "my", "here", "our"]

    def store_words_from_label(self, read_statement):
        """This function stores recognised words in csv files

        These files are associated with the label given to
        the word.

        Args:
            read_statement: the intelligence statement read into current python instance

        Returns
            Nothing - stores info in files
        """
        # Clean any leftover files from previous runs
        self.file_handler.clean_directory("data_files/target_info_files")
        text1 = NER(read_statement)

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

    def get_entities_and_count(self, text, entity_dict):
        """Finds the entities from the given text. If they appear multiple times, increment value.

        This only increments words one time per source. Only count independent mentions of entities.

        Args:
            text: The text to find and count entities from.
            entity_dict: The dictionary to store these entities and their respective counts in.

        Returns:
            entity_dict modified with new entries.
        """
        texts_length = len(text)
        print(texts_length)
        # split the text by factors of 50,000 to reduce memory load
        split_text = [text[i:i + 50000] for i in range(0, len(text), 50000)]
        entity_dict = self.add_entities_to_dict(entity_dict, split_text)

        return entity_dict

    def add_entities_to_dict(self, entity_dict, texts):
        words_present = []
        # just add entities to dictionary as each key needs to be unique.
        for doc in NER.pipe(texts):
            for ent in doc.ents:
                # set to lowercase for easy comparison
                key = ent.text.lower()
                # if the entity has not already been counted and is not an irrelevant word
                if (key not in words_present) and (key not in self.irrelevant_words):
                    try:
                        entity_dict[key] += 1
                    except KeyError:
                        entity_dict[key] = 1
                    words_present.append(key)

        return entity_dict
