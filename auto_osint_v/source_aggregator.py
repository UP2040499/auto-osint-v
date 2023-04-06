"""
Python Class for all functions of aggregating sources from open sources.
This includes using search engines (Google) and searching social media websites
(Twitter, Reddit, etc.)
"""
from tqdm import tqdm
from transformers import T5Tokenizer, T5ForConditionalGeneration
from googleapiclient.discovery import build


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
        # Google custom search engine API key and engine ID
        self.api_key = "AIzaSyCgsni4yZyp4Bla9J7a2TE-lxmzVagcjEo"
        self.cse_id = "d76b2d8504d104aa8"
        # list of social media sites - to add more insert the domain name here.
        self.social_media_sites = ["www.instagram.com", "www.tiktok.com", "www.facebook.com",
                                   "www.youtube.com", "www.reddit.com", "www.twitter.com",
                                   "www.pinterest.com", "www.github.com", "www.tumblr.com",
                                   "www.flickr.com", "www.steamcommunity.com", "vimeo.com",
                                   "medium.com", "vk.com", "imgur.com", "www.patreon.com",
                                   "bitbucket.org", "www.dailymotion.com", "news.ycombinator.com"]
        # Keywords here because they are used throughout the class
        self.keywords = self.file_handler.get_keywords_from_target_info()

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
        num_queries = 10    # number of queries to generate
        outputs = model.generate(
            input_ids=input_ids,
            max_length=128,  # default = 64
            do_sample=True,
            top_p=0.95,  # default = 0.95
            num_return_sequences=num_queries)  # Returns x queries, default = 3

        for i, output in enumerate(tqdm(outputs, desc="Generating Queries", total=num_queries)):
            query = tokenizer.decode(output, skip_special_tokens=True)
            self.queries.append(str(query))

    # the searcher method to search using a custom programmable search engine
    def searcher(self, search_term, **kwargs):
        service = build("customsearch", "v1", developerKey=self.api_key)
        res = service.cse().list(q=search_term, cx=self.cse_id, **kwargs).execute()
        try:
            return res['items']
        except KeyError:
            return []

    def write_url_to_txt_file(self, result, search_results_file):
        try:
            self.file_handler.write_to_txt_file_remove_duplicates(search_results_file,
                                                              result['link'])
        except KeyError:
            pass

    # Google Search
    def google_search(self):
        """

        :return:
        """
        search_results_file = self.file_handler.open_txt_file(self.search_results_filename)
        # Search google with given query and keyword, 10 results (10 per query & keyword).
        # tld could be changed to co.uk for better performance?
        for query in tqdm(self.queries, desc="Search Google using generated queries"):
            query_results = self.searcher(query, num=5)
            for result in query_results:
                self.write_url_to_txt_file(result, search_results_file)

        join_keywords = '|'.join(f'"{word}"' for word in self.keywords)
        keyword_results = self.searcher(f"(intext:{join_keywords})", num=10)
        for result in keyword_results:
            # write link to file
            self.write_url_to_txt_file(result, search_results_file)
        self.file_handler.close_file(search_results_file)

    # Social Media Search
    # reuse file_handler.write_to_txt_file_remove_duplicates method
    def social_media_search(self):
        """

        :return:
        """
        # open or create txt file to store search results
        search_results_file = self.file_handler.open_txt_file(self.search_results_filename)
        # Separate the social media results from Google search results
        self.file_handler.write_to_txt_file_remove_duplicates(search_results_file,
                                                              "\n--- Social Media ---")
        # can also specify more parameters for focusing on a particular location
        # see googlesearch.search()
        join_keywords = '|'.join(f'"{word}"' for word in self.keywords)
        for site in tqdm(self.social_media_sites, desc="Searching social media sites"):
            """
            for query in self.queries:
                for url in search(f"{query} site:{site}", tld="com", num=5, stop=5, pause=2):
                    # write url to file
                    self.file_handler.write_to_txt_file_remove_duplicates(search_results_file, url)
            """
            keyword_results = self.searcher(f"(site:{site}) (intext:{join_keywords})", num=10)
            for result in keyword_results:
                # write url to file
                self.write_url_to_txt_file(result, search_results_file)
        self.file_handler.close_file(search_results_file)

    def run_searches(self):
        """
        Runs the various search operations
        Note: keep the number of queries to a minimum in order to avoid getting IP blocked by google
        for too many requests.
        :return:
        """
        self.file_handler.clean_data_file(self.search_results_filename)
        # in both methods reduce number of queries
        # to search using a list of keywords put '%20OR%20' in between each element and search
        # this is a Google dorks technique to search for keyword OR next keyword etc.
        self.google_search()
        self.social_media_search()

    # Media Processor
    # interrogate each link and return a description of the media
    # i.e. text, video, image, sound, etc.
    # all media but text should go through the media processor
    # then retrieve the metadata for the media (if available)

    # Key information generator (likely using a BERT QA model)
    # need to keep in mind the resource cost of processing, given time and resource costs are
    # already high.

    # Sentiment analysis of key information and headlines
    # Very poor scores will lead to the source being discarded
    # Finally, store all potentially corroborating sources.

    # Will need a 'find_sources' method that runs all methods in this class.
