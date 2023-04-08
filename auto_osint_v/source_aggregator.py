"""
Python Class for all functions of aggregating sources from open sources.
This includes using search engines (Google) and searching social media websites
(Twitter, Reddit, etc.)
"""
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoModelForSeq2SeqLM, \
    AutoTokenizer
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
    def __init__(self, intel_statement, file_handler_object, sentiment_analyser_object):
        """
        Initialises the SourceAggregator object
        :param intel_statement: The original intel statement
        :param file_handler_object: The FileHandler object passed from main.py
        """
        self.intel_statement = intel_statement
        self.sentiment_analyser = sentiment_analyser_object
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
        # create the list of dictionaries
        self.results_list_dict = []

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
        This is the main processing step.
        Sentiment analysis is done to filter bias and inflammatory sources.
        By adjusting max_sentiment_threshold you may filter more sources
        (that are bias or inflammatory). Only change this if you find that sources retrieved appear
        bias or inflammatory, and vice versa, if it is filtering sources that do not appear very
        biased or inflammatory.
        :param result: Result type from Google Search API
        :return: nothing, stores info in instance dictionary variable
        """
        link = result['link']
        try:
            title = result['pagemap']['metatags'][0]['og:title']
        except KeyError:
            title = result['title']
        try:
            desc = result['pagemap']['metatags'][0]['og:description']
        except KeyError:
            desc = result['snippet']
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
        """
        if page_type == "article":
            website_summary = self.web_summary(link)
            self.results_dict["website_summary"].append(website_summary)
        """
        # sentiment analysis check - will discard headlines that appear inflammatory or bias
        # keep threshold relatively high (>0.8), see process_result() documentation.
        max_sentiment_threshold = 0.9
        label, score = self.sentiment_analyser.headline_analyser(title)
        # Very poor scores will lead to the source being discarded
        if not (label != "neutral" and score > max_sentiment_threshold):
            self.results_list_dict.append({"url": link, "title": title, "description": desc,
                                           "page_type": page_type, "time_published": publish_time,
                                           "image_links": images, "video_links": videos,
                                           "title_sentiment": f"{label} sentiment, score={score}"})

    def find_sources(self):
        """
        Runs the various search operations
        Note: keep the number of queries to a minimum in order to avoid getting IP blocked by google
        for too many requests.
        :return:
        """
        # in both methods reduce number of queries
        self.google_search()
        self.social_media_search()
        # store potentially corroborating sources in .csv file
        self.file_handler.create_potential_corroboration_file(self.results_list_dict)

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

    # Key information generator (likely using a BERT QA model)
    # need to keep in mind the resource cost of processing, given time and resource costs are
    # already high.

    # discarded for now as processing cost is too high, causes each URL lookup to take over a minute
    # *per url*, therefore these methods cannot be included in their current state.
    @staticmethod
    def url_get_text(url):
        """
        Gets the text from a website with given url
        :param url: the url to get the text from
        :return: the text from the website given by the url
        """
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup.get_text(strip=True)

    def web_summary(self, url):
        """
        Generates a summary of a given website.
        Summarisation code from HuggingFace Pegasus documentation.
        :return: the summary text
        """
        text = self.url_get_text(url)
        tokenizer = AutoTokenizer.from_pretrained("google/pegasus-large")
        model = AutoModelForSeq2SeqLM.from_pretrained("google/pegasus-large")

        inputs = tokenizer(text, truncation=True, return_tensors="pt")

        # Generate summary
        summary_ids = model.generate(inputs["input_ids"], max_new_tokens=1024)
        summary = tokenizer.batch_decode(summary_ids, skip_special_tokens=True,
                                         clean_up_tokenization_spaces=False)[0]
        return summary
