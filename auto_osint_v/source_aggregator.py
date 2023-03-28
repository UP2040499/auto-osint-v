"""
Python Class for all functions of aggregating sources from open sources.
This includes using search engines (Google) and searching social media websites
(Twitter, Reddit, etc.)
"""

import os
from transformers import T5Tokenizer, T5ForConditionalGeneration


class SourceAggregator:
    """
    Provides methods for aggregating sources (see module docstring).
    Most methods here will be private - not accessible by the rest of the program.
    This is because I want the aggregator to do all its work in one 'box' - likely more reusable as
    it can be shipped as a class with one input & one output.
    Everything output will be put into a 'Potential Corroboration Store'.
    """
    # Initialise object
    def __init__(self, intel_statement, data_folder):
        """
        Initialises the SourceAggregator object
        :param intel_statement: The original intel statement
        :param data_folder: Path to data_files folder
        """
        self.intel_statement = intel_statement
        self.data_file_path = data_folder
        self.queries = []

    # For searching, I think the key information needs to be extracted from the intel statement
    # Don't want to search using just the intel statement itself.
    # Statement keyword or key info generator (generating search query)
    def search_query_generator(self):
        """
        Creates a search query based on the intelligence statement, to be used in the search methods
        below.
        This is a resource (particularly memory) intensive process. Limit usage.
        Uses the BeIR/query-gen-msmarco-t5-large-v1 model and example code available on
        HuggingFace.co
        :return: List of queries
        """
        # Query generation based on the context of the intelligence statement
        tokenizer = T5Tokenizer.from_pretrained('BeIR/query-gen-msmarco-t5-large-v1')
        model = T5ForConditionalGeneration.from_pretrained('BeIR/query-gen-msmarco-t5-large-v1')
        # WARNING: If you are getting out of memory errors the model will need to be changed from
        # 'large' to 'base'.
        # If it is borderline try to change the max_length and num_return_sequences parameters
        # below.

        input_ids = tokenizer.encode(self.intel_statement, return_tensors='pt')
        outputs = model.generate(
            input_ids=input_ids,
            max_length=240,     # default = 64
            do_sample=True,
            top_p=0.95,         # default = 0.95
            num_return_sequences=10)  # Returns x queries, default = 3

        print("\nGenerated Queries:")
        for i, output in enumerate(outputs):
            query = tokenizer.decode(output, skip_special_tokens=True)
            # self.queries.append(str(query))
            print(f'{i + 1}: {query}')

    # Google Search

    # Social Media Search

    # Video Processor

    # Semantic analysis of whole document

    # Key information generator (likely using BERT QA)
    # Should try to make reusable (key info from statement and key info from sources)

    # Sentiment analysis of key information and headlines
    # Very poor scores will lead to the source being discarded
    # Finally, store all potentially corroborating sources.

    # Will need a 'find_sources' method that runs all methods in this class.
