"""
This module forms the main part of the program, where other modules are run from.
"""

import os
from specific_entity_processor import EntityProcessor
from file_handler import FileHandler
from semantic_analyser import SemanticAnalyser

data_file_path = os.getcwd() + "/data_files/"


def input_intelligence():
    """
    This method creates a text file for the user to input their intelligence statement into.
    """
    print("A notepad window will now open in your default text editor.")
    print("Please enter the intelligence statement in there and save the file.\n")
    file_handler.write_intel_file()


def input_bias_sources():
    """
    This function will create a csv file for the bias sources to be stored in.
    """
    print("Enter a Bias Source")
    print("You will now be asked to enter any sources you believe are important to compare to.")
    print("This allows other sources of intelligence"
          "(such as closed or classified sources) to be compared.")
    option = str(input("Press ENTER to continue or press 'X' to skip this step. >>> "))
    if option not in {"x", "X"}:
        file_handler.write_bias_file()


if __name__ == '__main__':
    # This code won't run if this file is imported.
    file_handler = FileHandler(data_file_path)
    #input_intelligence()
    #input("\nPress ENTER to continue...\n")
    #input_bias_sources()
    #test_object = EntityProcessor(file_handler.read_file("intelligence_file.txt"), file_handler)
    #test_object.store_words_from_label()
    # call to semantic analyser
    analyse_sentiment_object = SemanticAnalyser(file_handler.read_file("intelligence_file.txt"))
    analyse_sentiment_object.statement_analyser()
