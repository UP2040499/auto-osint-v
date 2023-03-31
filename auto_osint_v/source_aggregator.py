"""
Python Class for all functions of aggregating sources from open sources.
This includes using search engines (Google) and searching social media websites
(Twitter, Reddit, etc.)
"""

from transformers import T5Tokenizer, T5ForConditionalGeneration
from googlesearch import search


class SourceAggregator:
    """
    Provides methods for aggregating sources (see module docstring).
    Most methods here will be private - not accessible by the rest of the program.
    This is because I want the aggregator to do all its work in one 'box' - likely more reusable as
    it can be shipped as a class with one input & one output.
    Everything output will be put into a 'Potential Corroboration Store'.
    """

    # Initialise object
    def __init__(self, intel_statement, file_handler_object):
        """
        Initialises the SourceAggregator object
        :param intel_statement: The original intel statement
        :param file_handler_object: The FileHandler object passed from main.py
        """
        self.intel_statement = intel_statement
        self.file_handler = file_handler_object
        self.search_results_filename = "search_results.txt"
        self.queries = []
        # list of social media sites - to add more insert the domain name here.
        self.social_media_sites = ["www.instagram.com", "www.tiktok.com", "www.facebook.com",
                                   "www.youtube.com", "www.reddit.com", "www.twitter.com",
                                   "www.pinterest.com", "www.github.com", "www.tumblr.com",
                                   "www.flickr.com", "www.steamcommunity.com", "vimeo.com",
                                   "medium.com", "vk.com", "imgur.com", "www.patreon.com",
                                   "bitbucket.org", "www.dailymotion.com", "news.ycombinator.com"]

    # For searching, I think the key information needs to be extracted from the intel statement
    # Don't want to search using just the intel statement itself.
    # Statement keyword or key info generator (generating search query)
    def search_query_generator(self):
        """
        Creates a search query based on the intelligence statement, to be used in the search methods
        below.
        This is a resource (particularly memory) intensive process. Limit usage.
        Uses the BeIR/query-gen-msmarco-t5-large-v1 pre-trained model and example code available on
        HuggingFace.co
        Currently uses the 'large' model for accuracy. This can be downgraded to 'base' for reduced
        accuracy but better performance.
        :return: List of queries
        """
        # Query generation based on the context of the intelligence statement
        tokenizer = T5Tokenizer.from_pretrained('BeIR/query-gen-msmarco-t5-large-v1')
        model = T5ForConditionalGeneration.from_pretrained('BeIR/query-gen-msmarco-t5-large-v1')
        # WARNING: If you are getting out of memory errors the model will need to be changed from
        # 'large' to 'base'.
        # Potential future fix to this problem - wrap in a try-except to auto switch to base model.
        # If it is borderline try to change the max_length and num_return_sequences parameters
        # below.

        input_ids = tokenizer.encode(self.intel_statement, return_tensors='pt')
        outputs = model.generate(
            input_ids=input_ids,
            max_length=128,  # default = 64
            do_sample=True,
            top_p=0.95,  # default = 0.95
            num_return_sequences=10)  # Returns x queries, default = 3

        print("\nGenerated Queries:")
        for i, output in enumerate(outputs):
            query = tokenizer.decode(output, skip_special_tokens=True)
            self.queries.append(str(query))
            print(f'{i + 1}: {query}')

    # Google Search
    def google_search(self):
        """

        :return:
        """
        search_results_file = self.file_handler.open_txt_file(self.search_results_filename)
        # Search google with given query, 10 results (10 per query).
        # tld could be changed to co.uk for better performance?
        for query in self.queries:
            for url in search(query, tld="com", num=10, stop=10, pause=2):
                self.file_handler.write_to_txt_file_remove_duplicates(search_results_file, url)

        # For greater accuracy we should just get keywords from the statement and use those

        self.file_handler.close_file(search_results_file)

    # Social Media Search
    # reuse file_handler.write_to_txt_file_remove_duplicates method
    def social_media_search(self):
        """

        :return:
        """
        from Scweet.scweet import scrape
        # open or create txt file to store search results
        search_results_file = self.file_handler.open_txt_file(self.search_results_filename)

        # we can also specify more parameters for focusing on a particular location
        # see googlesearch.search()
        for query, site in zip(self.queries, self.social_media_sites):
            for url in search(f"{query} site:{site}", tld="com", num=10, stop=10, pause=2):
                # do operation with url
                self.file_handler.write_to_txt_file_remove_duplicates(search_results_file, url)
        self.file_handler.close_file(search_results_file)

        # potential future addition: username search using ncorbuk's Looking Glass python tool
        # https://github.com/ncorbuk/Python-Tutorial---Hunt-Down-Social-Media-Accounts-by-Usernames-for-Open-Source-Intelligence-

    def run_searches(self):
        self.file_handler.clean_data_file(self.search_results_filename)
        self.google_search()
        self.social_media_search()

    # Video Processor

    # Semantic analysis of whole document

    # Key information generator (likely using BERT QA)
    # Should try to make reusable (key info from statement and key info from sources)

    # Sentiment analysis of key information and headlines
    # Very poor scores will lead to the source being discarded
    # Finally, store all potentially corroborating sources.

    # Will need a 'find_sources' method that runs all methods in this class.
    def get_social_media_sites(self):
        return self.social_media_sites
