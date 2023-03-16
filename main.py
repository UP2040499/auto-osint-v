"""
This module forms the main part of the program, where other modules are run from.
"""

import os
import webbrowser
import csv
from specific_entity_processor import EntityProcessor
from file_handler import FileHandler

data_file_path = os.getcwd() + "/DataFiles/"

def input_intelligence():
    """
    This method creates a text file for the user to input their intelligence statement into.
    """
    print("Intelligence statement help:\n")
    print("- Please include as much information as possible\n")
    print("- If an entity is a person please include known associates\n")
    print("A notepad window will now open - enter the intelligence statement in there.")
    file_handler.write_intel_file()

def input_bias_sources():
    """
    This function will create a csv file for the bias sources to be stored in.
    """
    print("Enter a Bias Source")
    print("You will now be asked to enter any sources you believe are important to compare to.")
    print("This allows other sources of intelligence \
          (such as closed or classified sources) to be compared.")
    option = " " + str(input("Press ENTER to continue or press 'X' to skip this step. >>> "))
    if option in {"x", "X"}:
        return
    file_handler.write_bias_file()

if __name__ == '__main__':
    # This code won't run if this file is imported.
    file_handler = FileHandler(data_file_path)
    input_intelligence()
    input("Press enter to continue")
    input_bias_sources()
    test_object = EntityProcessor(file_handler.read_file("intelligence_file.txt"))
    test_object.test_func()
