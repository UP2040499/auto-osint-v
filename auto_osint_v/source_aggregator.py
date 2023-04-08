"""
Python Class for all functions of aggregating sources from open sources.
This includes using search engines (Google) and searching social media websites
(Twitter, Reddit, etc.)
"""
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
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
        # create the dictionary using given keys
        self.results_dict = {"url": [], "title": [], "description": [], "page_type": [],
                             "time_published": [], "image_links": [], "video_links": []}

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
        num_queries = 10  # number of queries to generate
        outputs = model.generate(
            input_ids=input_ids,
            max_length=128,  # default = 64
            do_sample=True,
            top_p=0.95,  # default = 0.95
            num_return_sequences=num_queries)  # Returns x queries, default = 3

        for i, output in enumerate(outputs):
            query = tokenizer.decode(output, skip_special_tokens=True)
            self.queries.append(str(query))

    # the searcher method to search using a custom programmable search engine
    def searcher(self, search_term, **kwargs):
        """
        Using the Google Custom Search Engine to search for results to the search_term.
        :param search_term: The keyword/query to search for
        :param kwargs: Extra arguments to pass to service.cse().list
        :return:
        """
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
        Searches google using both the generated queries, and the extracted keywords.
        Limits the number of queries sent to google where possible.
        Uses the Google Custom Search Engine
        :return: dictionary of Google search results
        """
        # define dictionary index used to store results
        dict_index = 0
        # searches google using the generated queries
        for query in tqdm(self.queries, desc="Search Google using generated queries"):
            # one search per query
            query_results = self.searcher(query, num=5)
            for result in query_results:
                # write link to dict
                self.process_result(result)
        # Join the list of keywords/phrases into one string seperated by '|' and surrounded by ""
        join_keywords = '|'.join(f'"{word}"' for word in self.keywords)
        # Get the results from one query using the list of keywords
        keyword_results = self.searcher(f"(intext:{join_keywords})", num=10)
        # loop through results
        for result in tqdm(keyword_results, desc="Search Google using extracted keywords"):
            # write link to dict
            self.process_result(result)

    # Social Media Search
    # reuse file_handler.write_to_txt_file_remove_duplicates method
    def social_media_search(self):
        """

        :return: dictionary storing the social media results
        """
        # define dictionary to store results
        # Join the list of keywords/phrases into one string seperated by '|' and surrounded by ""
        join_keywords = '|'.join(f'"{word}"' for word in self.keywords)
        # Loop through list of social media sites
        for site in tqdm(self.social_media_sites, desc="Searching social media sites"):
            """
            for query in self.queries:
                for url in search(f"{query} site:{site}", tld="com", num=5, stop=5, pause=2):
                    # write url to file
                    self.file_handler.write_to_txt_file_remove_duplicates(search_results_file, url)
            """
            # search for the keywords using one google query
            keyword_results = self.searcher(f"(site:{site}) (intext:{join_keywords})", num=10)
            # loop through results
            for result in keyword_results:
                # get process the result
                self.process_result(result)
        # return # dict

    def process_result(self, result):
        """
        Takes the result from the search, extracts information and saves it all in a dictionary.
        :param result: Result type from Google Search API
        :return: nothing, stores info in instance dictionary variable
        """
        link = result['link']
        title = result['title']
        snippet = result['snippet']
        try:
            page_type = result['pagemap']['metatags'][0]['og:type']
        except KeyError:
            page_type = ""
        try:
            publish_time = result['pagemap']['metatags'][0]['article:published_time']
        except KeyError:
            publish_time = ""
        try:
            images, videos = self.media_finder(link)
        except requests.exceptions.SSLError:
            images, videos = [], []
        self.results_dict["url"].append(link)
        self.results_dict["title"].append(title)
        self.results_dict["description"].append(snippet)
        self.results_dict["page_type"].append(page_type)
        self.results_dict["time_published"].append(publish_time)
        self.results_dict["image_links"].append(images)
        self.results_dict["video_links"].append(videos)

    def run_searches(self):
        """
        Runs the various search operations
        Note: keep the number of queries to a minimum in order to avoid getting IP blocked by google
        for too many requests.
        :return:
        """
        # in both methods reduce number of queries
        # to search using a list of keywords put '%20OR%20' in between each element and search
        # this is a Google dorks technique to search for keyword OR next keyword etc.
        self.google_search()
        self.social_media_search()

    # Media Processor
    # interrogate each link and return a description of the media
    # i.e. text, video, image.
    # all media but text should go through the media processor
    # then retrieve the metadata for the media (if available)
    @staticmethod
    def find_images(soup):
        """
        Finds images in a given HTML document
        :param soup: Parsed HTML
        :return:
        """
        image_urls = []
        images = soup.find_all("img")
        for image in images:
            image_url = image.get("src")
            image_urls.append(image_url)
        return image_urls

    @staticmethod
    def find_videos(soup):
        """
        Finds images in a given HTML document
        :param soup: Parsed HTML
        :return:
        """
        video_urls = []
        videos = soup.find_all("video")
        for video in videos:
            video_url = video.get("src")
            video_urls.append(video_url)
        return video_urls

    def media_finder(self, url):
        """
        Finds media in the HTML from the given URL. This finds images and videos.
        :param url: The URL for the website
        :return: The info we want: website title, description, images & videos
        """
        # retrieve html from URL
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # image and video tags may not be in the website.
        try:
            images = self.find_images(soup)
        except KeyError:
            images = []
        try:
            videos = self.find_videos(soup)
        except KeyError:
            videos = []
        return images, videos

    # It may be impossible but if there is a way to find any website's 'last-updated' date
    # This would be a helpful metric for determining relevance.
    # Currently, I do not think this is possible for *any* website, but it may work for some.
    # It is also possible to change the searching methods to only find results from a given date
    # interval.

    # Key information generator (likely using a BERT QA model)
    # need to keep in mind the resource cost of processing, given time and resource costs are
    # already high.

    # Sentiment analysis of key information and headlines
    # Very poor scores will lead to the source being discarded
    # Finally, store all potentially corroborating sources.

    # Will need a 'find_sources' method that runs all methods in this class.
