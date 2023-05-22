"""Python Class for all functions of aggregating sources from open sources.

This includes using search engines (Google) and searching social media websites
(Twitter, Reddit, etc.)
"""
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from transformers import T5Tokenizer, T5ForConditionalGeneration
from googleapiclient.discovery import build


class SourceAggregator:
    """Provides methods for aggregating sources (see module docstring).

    Most methods here will be private - not accessible by the rest of the program.
    This is because I want the aggregator to do all its work in one 'box' - likely more reusable as
    it can be shipped as a class with one input & one output.
    Everything output will be put into a 'Potential Corroboration Store'.
    """

    # Initialise object
    def __init__(self, intel_statement, file_handler_object, sentiment_analyser_object):
        """
        Initialises the SourceAggregator object.

        Args:
            intel_statement: The original intel statement
            file_handler_object: The FileHandler object passed from __main__.py
        """
        self.intel_statement = intel_statement
        self.sentiment_analyser = sentiment_analyser_object
        self.file_handler = file_handler_object
        self.queries = []
        # Keywords here because they are used throughout the class
        self.keywords = self.file_handler.get_keywords_from_target_info()
        # create the list of dictionaries
        self.results_list_dict = []
        # list to store unique urls
        self.urls_present = []

    # For searching, I think the key information needs to be extracted from the intel statement
    # Don't want to search using just the intel statement itself.
    # Statement keyword or key info generator (generating search query)
    def search_query_generator(self):
        """Generates a search queries based on the given statement.

        This is a resource (particularly memory) intensive process. Limit usage.
        Uses the BeIR/query-gen-msmarco-t5-large-v1 pre-trained model and example code available on
        HuggingFace.co
        Currently uses the 'large' model for accuracy. This can be downgraded to 'base' for reduced
        accuracy but better performance.

        Returns:
            List of queries
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
        # number of queries to generate - increase in this massively impact performance
        num_queries = 3
        outputs = model.generate(
            input_ids=input_ids,
            max_length=128,  # default = 64
            do_sample=True,
            top_p=0.95,  # default = 0.95
            num_return_sequences=num_queries)  # Returns x queries, default = 3

        for output in outputs:
            query = tokenizer.decode(output, skip_special_tokens=True)
            self.queries.append(str(query))

    # the searcher method to search using a custom programmable search engine
    @staticmethod
    def searcher(search_term, **kwargs):
        """Using the Google Custom Search Engine to search for results to the search_term.

        Args:
            search_term: The keyword/query to search for. This can be a string or a list of strings.
            kwargs: Extra arguments to pass to service.cse().list

        Returns:
            the results or nothing if none are found.
        """
        # Google custom search engine API key and engine ID
        api_key = "AIzaSyCgsni4yZyp4Bla9J7a2TE-lxmzVagcjEo"
        cse_id = "d76b2d8504d104aa8"
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, hl='en', **kwargs).execute()
        try:
            return res['items']
        except KeyError:
            # print("No results found for query:", search_term)
            return []

    # Google Search
    def google_search(self):
        """Searches google using both the generated queries, and the extracted keywords.

        Limits the number of queries sent to google where possible.
        Uses the Google Custom Search Engine

        Returns:
            dictionary of Google search results
        """
        query_results = []
        for query in self.queries:
            # searches google using the generated queries
            query_results += self.searcher(query, num=3)
        for result in tqdm(query_results, desc="Search Google using generated queries"):
            # write link to dict
            self.process_result(result)
        # search for the keywords, only 7 at a time
        keyword_results = []
        length_of_split = 7
        split_keywords = [self.keywords[i:i + length_of_split]
                          for i in range(0, len(self.keywords), length_of_split)]
        for keywords in split_keywords:
            keyword_results += self.searcher(keywords, num=10//len(split_keywords))
        # loop through results
        for result in tqdm(keyword_results, desc="Search Google using extracted keywords"):
            # write link to dict
            self.process_result(result)

    # Social Media Search
    # reuse file_handler.write_to_txt_file_remove_duplicates method
    def social_media_search(self):
        """Searches a variety of social media sites see 'social_media_sites' variable.

        WARNING: To search using generated queries and extracted keywords, the code has nested for
        loops.
        Significant performance boost achieved by finding out that the 'q' parameter for cse.list
        takes lists as well as strings.

        Returns:
            dictionary storing the social media results
        """
        # define social media sites - to add more insert the domain name here.
        social_media_sites = ["www.instagram.com", "www.tiktok.com", "www.facebook.com",
                              "www.youtube.com", "www.reddit.com", "www.twitter.com",
                              "www.pinterest.com", "www.github.com", "www.tumblr.com",
                              "www.flickr.com", "vimeo.com", "www.telegram.com"
                              "medium.com", "vk.com", "imgur.com", "www.patreon.com",
                              "bitbucket.org", "www.dailymotion.com", "news.ycombinator.com"]
        # Join the list of keywords/phrases into one string seperated by '|' and surrounded by ""
        # it appears that the max number of comparisons is between 7 and 10.
        # google documentation says it should be 10
        # join_keywords = '|'.join(f'"{word}"' for word in self.keywords)
        # Loop through list of social media sites
        for site in tqdm(social_media_sites, desc="Searching Social Media Sites"):
            # this for loop is clearly inefficient, I don't know how to improve it
            # I'm unsure of this behaviour as the siteSearch parameter doesn't seem to work
            query_results = self.searcher(self.queries, siteSearch=site, siteSearchFilter='i',
                                          num=5)
            # loop through results
            for result in query_results:
                # write link to dict
                self.process_result(result)
            # search for the keywords, only 7 at a time
            keyword_results = []
            length_of_split = 7
            split_keywords = [self.keywords[i:i + length_of_split]
                              for i in range(0, len(self.keywords), length_of_split)]
            for keywords in split_keywords:
                keyword_results += self.searcher(keywords, siteSearch=site,
                                                 siteSearchFilter='i', num=5)
            for result in keyword_results:
                # get process the result
                self.process_result(result)

    def process_result(self, result):
        """Takes the result from the search, extracts information and saves it all in a dictionary.

        This is the main processing step.
        Sentiment analysis is done to filter bias and inflammatory sources.
        By adjusting max_sentiment_threshold you may filter more sources
        (that are bias or inflammatory). Only change this if you find that sources retrieved appear
        bias or inflammatory, and vice versa, if it is filtering sources that do not appear very
        biased or inflammatory.

        Args:
            result: Result type from Google Search API

        Returns:
            nothing, stores info in instance dictionary variable
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
            iframes, images, videos = self.media_finder(link)
        except (requests.exceptions.SSLError, requests.exceptions.Timeout):
            iframes, images, videos = "NaN", "NaN", "NaN"
        # sentiment analysis check - will discard headlines that appear inflammatory or bias
        # keep threshold relatively high (>0.8), see process_result() documentation.
        max_sentiment_threshold = 0.9
        label, score = self.sentiment_analyser.headline_analyser(title)
        # discard any duplicates
        if link not in self.urls_present:
            self.urls_present.append(link)
            # Very poor scores will lead to the source being discarded
            if not (label != "neutral" and score > max_sentiment_threshold):
                self.results_list_dict.append({"url": link, "title": title, "description": desc,
                                               "page_type": page_type,
                                               "time_published": publish_time,
                                               "image_links": images, "video_links": videos,
                                               "embedded_content": iframes,
                                               "title_sentiment":
                                                   f"{label} sentiment, score={score}"})

    def find_sources(self):
        """Runs the various search operations.

        Returns:
            results in the form of a list of dictionaries
        """
        # in both methods reduce number of queries
        self.google_search()
        self.social_media_search()
        # store potentially corroborating sources in .csv file
        self.file_handler.create_potential_corroboration_file(self.results_list_dict)
        return self.results_list_dict

    # Media Processor
    # interrogate each link and return a description of the media
    # i.e. text, video, image.
    # all media but text should go through the media processor
    # then retrieve the metadata for the media (if available)
    @staticmethod
    def find_images(soup):
        """Finds images in a given HTML document.

        Args:
            soup: Parsed HTML

        Returns:
            source URLs for the images
        """
        image_urls = []
        images = soup.find_all("img")
        for image in images:
            image_urls.append(image.get("src"))
        return image_urls

    @staticmethod
    def find_videos(soup):
        """Finds images in a given HTML document.

        Args:
            soup: Parsed HTML

        Returns:
            source URLs for the videos
        """
        video_urls = []
        videos = soup.find_all("video")
        for video in videos:
            video_urls.append(video.get("src"))
        return video_urls

    @staticmethod
    def find_iframes(soup):
        """Finds embedded content in iframes, in a given HTML document.

        Args:
            soup: Parsed HTML

        Returns:
            source URLs for the content
        """
        iframe_urls = []
        iframes = soup.find_all("iframe")
        for iframe in iframes:
            iframe_urls.append(iframe.get("src"))
        return iframe_urls

    def media_finder(self, url):
        """Finds media in the HTML from the given URL. This finds images and videos.

        Args:
            url: The URL for the website

        Returns:
            The info we want: website title, description, images & videos
        """
        # retrieve html from URL
        response = requests.get(url, timeout=10)  # timeout 10 seconds
        # get the content type
        try:
            content_type = response.headers['Content-Type']
            # if xml use xml parser
            if content_type == "text/xml" or content_type == "application/xml":
                # use xml parser
                soup = BeautifulSoup(response.text, "xml")
            else:
                # parse using the lxml html parser
                soup = BeautifulSoup(response.text, "lxml")
        except KeyError:
            # except on KeyError if no 'content-type' header exists
            soup = BeautifulSoup(response.text, "lxml")
        # image and video tags may not be in the website.
        try:
            images = self.find_images(soup)
        except KeyError:
            images = []
        try:
            videos = self.find_videos(soup)
        except KeyError:
            videos = []
        try:
            iframes = self.find_iframes(soup)
        except KeyError:
            iframes = []
        return images, videos, iframes
