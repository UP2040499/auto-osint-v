"""This module forms the main part of the program, where other modules are run from.

Run this file to run the tool.
"""
import os
import sys
from itertools import combinations
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import argparse
import pandas as pd
from typing import List

from auto_osint_v.specific_entity_processor import EntityProcessor
from auto_osint_v.file_handler import FileHandler
from auto_osint_v.sentiment_analyser import SentimentAnalyser
from auto_osint_v.source_aggregator import SourceAggregator
from auto_osint_v.priority_manager import PriorityManager

data_file_path = os.getcwd() + "/data_files/"
sys.path.append(
    "/auto_osint_v/main.py")
# modify environment variables
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
os.environ['TOKENIZERS_PARALLELISM'] = 'false'


def input_intelligence(editor: bool):
    """This method creates a text file for the user to input their intelligence statement into.
    """
    print("You will now be directed to enter the intelligence statement.")
    if editor:
        print("Please enter the intelligence statement in the text editor window that has opened"
              "and save the file.\n")
    else:
        print("Please enter the intelligence statement into the command line.")
    file_handler.write_intel_file(editor)


def input_bias_sources(sentiment_analyser):
    """This function will create a csv file for the bias sources to be stored in.
    """
    print("Enter a source for your intelligence statement")
    print("Your source can be of any form.")
    print("This allows other sources of intelligence"
          "(such as closed or classified sources) to be compared.")
    option = str(input("Press ENTER to continue or press 'X' to skip this step. >>> "))
    if option not in {"x", "X"}:
        file_handler.write_bias_file(sentiment_analyser.headline_analyser)


def similar(a, b, threshold=0.90):
    """Determines if two sources are similar to each other
    Args:
        a: first url to compare
        b: second url to compare
        threshold: Optional max similarity threshold for documents

    Returns:
        Boolean True or False
    """
    priority_manager = PriorityManager
    text1, text2 = map(priority_manager.get_text_from_site, (a, b))
    # split the texts every 500 chars
    text1_split = [text1[i:i + 500] for i in range(0, len(text1), 500)]
    text2_split = [text2[i:i + 500] for i in range(0, len(text2), 500)]
    # for each 'sentence' in both texts generate similarity scores
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings1 = model.encode(text1_split, convert_to_tensor=True)
    embeddings2 = model.encode(text2_split, convert_to_tensor=True)

    cosine_scores = util.cos_sim(embeddings1, embeddings2)
    # print(f"{embeddings1}\n{embeddings2}\n\n{cosine_scores}")
    # get maximum similarity (see BERTscore paper)
    # Find the pairs with the highest cosine similarity scores
    pairs = []
    for i in range(cosine_scores.shape[0]):
        for j in range(cosine_scores.shape[1]):
            pairs.append({'index': [i, j], 'score': cosine_scores[i][j]})

    # Sort scores in decreasing order
    pairs = sorted(pairs, key=lambda x: x['score'], reverse=True)
    highest_score = pairs[0]
    print(highest_score['score'])
    if highest_score['score'] > threshold:
        return True
    else:
        return False


def similarity_check(sources):
    """Check the similarity of the top sources that will be output.

    If a source is similar to another, remove the source with the lowest score.

    BROKEN: seems to make results distinct, but at the cost of relevance. (not acceptable)

    Args:
        sources: the list of sources to examine
    """
    output_sources = sources[:10]
    sources = sources[10:]
    for source_a, source_b in tqdm(combinations(output_sources, 2),
                                   total=len(list(combinations(output_sources, 2))),
                                   desc="Checking source similarity, removing similar sources."):
        if similar(source_a['url'], source_b['url']):  # optional parameter threshold available
            # assuming scores of source_a > scores of source_b
            try:
                output_sources.remove(source_b)  # remove the lowest scoring source
            except ValueError:
                return output_sources
            next_source = sources[0]
            i = 1
            while similar(source_a['url'], next_source['url']):
                next_source = sources[i]
                sources = sources[i:]
                i += 1
                if i > len(sources):
                    break
            output_sources.append(next_source)  # add next highest source
            sources = sources[1:]
    return output_sources


def format_output(source_list_dict: List[dict], file_handler_obj):
    """Formats all the results into a table.

    This takes the sources, bias sources (if any), sentiment analysis results

    Returns:
        the output dataframe, which can be printed
    """
    output = str()
    # get sentiment analysis results from evidence file
    sentiment_dict = file_handler_obj.read_evidence_file()[0]
    # get bias sources from bias file
    bias_list_dict = file_handler_obj.read_bias_file()
    # create the dataframe for all our results
    dataframe = pd.DataFrame(columns=["Evidence Type", "Important Info", "URL", "Extra Info",
                                      "Priority Score", "Headline Sentiment"])
    # add sentiment analysis of statement to dataframe
    dataframe = dataframe.append({"Evidence Type": sentiment_dict["evidence type"],
                                  "Important Info": sentiment_dict["info"]})
    # add bias sources to the dataframe
    for bias_dict in bias_list_dict:
        dataframe = dataframe.append({"Evidence Type": bias_dict["Type/Link"],
                                      "Important Info": bias_dict["Key Info"],
                                      "Headline Sentiment": bias_dict["Info Sentiment"]})
    # add corroborating sources to the dataframe
    for source in source_list_dict:
        dataframe = dataframe.append({"Evidence Type": "Corroboration",
                                      "Important Info": source["title"],
                                      "URL": source["url"],
                                      "Extra Info": source["description"] + " Page Type: " +
                                      source["page_type"] + " Published on: " +
                                      source["time_published"],
                                      "Priority Score": source["score"],
                                      "Headline Sentiment": source["title_sentiment"]
                                      })
    return dataframe


if __name__ == '__main__':
    # interpret command line arguments
    parser = argparse.ArgumentParser()
    # add optional arguments
    parser.add_argument("-s", "--Silent", help="Assumes you have already entered the intelligence"
                                               "statement in "
                                               "auto_osint_v/data_files/intelligence_file.txt")
    parser.add_argument("-n", "--NoEditor", help="Input intelligence statement into command line"
                                                 "rather than into text editor.")
    # read args from command line
    args = parser.parse_args()
    # This code won't run if this file is imported.
    file_handler = FileHandler(data_file_path)
    # Only input point for user - potential refinement would be a feedback loop to the user.
    use_editor = True
    if args.NoEditor:
        use_editor = False
    if not args.Silent:
        input_intelligence(use_editor)
        input("\nPress ENTER to continue...\n")
    else:
        print("Intelligence statement already entered, skipping...")
    intel_file = ""
    analyse_sentiment_object = SentimentAnalyser(intel_file, "intelligence_statement", file_handler)
    input_bias_sources(analyse_sentiment_object)
    # Read intelligence file
    print("Reading intelligence file...")
    intel_file = file_handler.read_file("intelligence_file.txt")
    # set the statement parameter
    analyse_sentiment_object.set_statement(intel_file)
    # Entity Processor - identifies specific entities mentioned in intel statement
    print("Processing entities...")
    process_entities = EntityProcessor(file_handler)
    process_entities.store_words_from_label(intel_file)

    # Clean evidence_file.csv
    file_handler.clean_data_file(data_file_path + "evidence_file.csv")
    # call to sentiment analyser - sentiment analysis on intel statement
    print("Analysing sentiment of intelligence statement...")
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
    priority_manager = PriorityManager(file_handler, process_entities, potential_sources)
    # Check the relevance of sources, filter out those that are not relevant.
    # Assign higher priority (order) to sources that are most relevant.
    sources = priority_manager.manager()
    # print([f"url: {source['url']}, score: {source['score']}" for source in sources])

    # similarity_check(sources) - does not work, unfortunately.

    # OUTPUT:
    out_df = format_output(sources, file_handler)
    # we can turn sources into a pandas dataframe then use df.style or display(df) or tabulate(df)
    # display the dataframe
    out_df.style

    # TODO:
    #   ~~~~~ High Priority ~~~~~
    #   Add nice formatting to output (tabular, colour optional)
    #   Reformat the 'bias source checker' so that it asks for any sources of the intelligence
    #   Source similarity goes just before the output. These branches can be merged into one.
    #   ~~~~~ Low Priority ~~~~~
    #   Assign scores to the bias sources too.
    #   Attempt to fix sentence indices out of range warning (popular info finder).
    #   Attempt to solve the imgur sitemap problem (easy way: remove links to xml)
    #   Solve issues with irrelevant output (possibly change formatting of source text)
    #   Allow auto_osint_v.main to be called from command line, with the intelligence file as param.
    #       This means either input through command line or ask for them to modify the file.
    #       I believe that input into the command line will be difficult, so stick with modifying
    #       file in their editor. Ask for user to modify file on first run.
    #       This could mean having a 'silent' or 'no_editor' mode for the user to run if they have
    #       already changed the intelligence file.
