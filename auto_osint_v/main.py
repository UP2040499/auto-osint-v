"""This module forms the main part of the program, where other modules are run from.

Run this file to run the tool.
"""
import os
import sys
from auto_osint_v.specific_entity_processor import EntityProcessor
from auto_osint_v.file_handler import FileHandler
from auto_osint_v.sentiment_analyser import SemanticAnalyser
from auto_osint_v.source_aggregator import SourceAggregator
from auto_osint_v.popular_information_finder import PopularInformationFinder
from auto_osint_v.priority_manager import PriorityManager

data_file_path = os.getcwd() + "/data_files/"
sys.path.append(
    "/auto_osint_v/main.py")

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"


def input_intelligence():
    """This method creates a text file for the user to input their intelligence statement into.
    """
    print("A notepad window will now open in your default text editor.")
    print("Please enter the intelligence statement in there and save the file.\n")
    file_handler.write_intel_file()


def input_bias_sources():
    """This function will create a csv file for the bias sources to be stored in.
    """
    print("Enter a source for your intelligence statement")
    print("Your source can be of any form.")
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
    print("Reading intelligence file...")
    intel_file = file_handler.read_file("intelligence_file.txt")
    # Entity Processor - identifies specific entities mentioned in intel statement
    print("Processing entities...")
    process_entities = EntityProcessor(file_handler)
    process_entities.store_words_from_label(intel_file)

    # Clean evidence_file.csv
    file_handler.clean_data_file(data_file_path + "evidence_file.csv")
    # call to sentiment analyser - sentiment analysis on intel statement
    print("Analysing sentiment of intelligence statement...")
    analyse_sentiment_object = SemanticAnalyser(intel_file, "intelligence_statement", file_handler)
    analyse_sentiment_object.statement_analyser()
    # Source aggregation below
    print("\nAggregating Sources:")
    source_aggregator = SourceAggregator(intel_file, file_handler, analyse_sentiment_object)
    # generates 10 queries and stores it in the source_aggregator object
    print("Generating queries...")
    source_aggregator.search_query_generator()
    # Searches google and social media sites using the queries stored in source_aggregator object
    # search results will be stored in a dictionary in the source_aggregator Object.
    potential_sources = source_aggregator.find_sources()
    # Initialise the Priority Manager
    priority_manager = PriorityManager(file_handler, potential_sources)

    # get the popular information - this is a costly search (on 170 sources it takes ~15 minutes).
    # print(popular_information_finder.find_entities(potential_sources))
