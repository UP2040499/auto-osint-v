"""
This module forms the main part of the program, where other modules are run from.
"""

import os
import sys
from specific_entity_processor import EntityProcessor
from file_handler import FileHandler
from sentiment_analyser import SentimentAnalyser
from source_aggregator import SourceAggregator

data_file_path = os.getcwd() + "/data_files/"
sys.path.append("/auto_osint_v/main.py")


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
    # Only input point for user - potential refinement would be a feedback loop to the user.
    input_intelligence()
    input("\nPress ENTER to continue...\n")
    input_bias_sources()
    # Read intelligence file
    intel_file = file_handler.read_file("intelligence_file.txt")
    # Entity Processor - identifies specific entities mentioned in intel statement
    process_entities = EntityProcessor(intel_file, file_handler)
    process_entities.store_words_from_label()
    # Clean evidence_file.csv
    os.remove(data_file_path+"evidence_file.csv")
    # call to semantic analyser - sentiment analysis on intel statement
    analyse_sentiment_object = SentimentAnalyser(intel_file, "intelligence_statement", file_handler)
    analyse_sentiment_object.statement_analyser()
    # Source aggregation below
    source_aggregator = SourceAggregator(intel_file, data_file_path)
    source_aggregator.search_query_generator()
    