"""Finds entities (information) that is popular amongst the potentially corroborating sources.
"""
import http.client
import itertools
from multiprocessing import Pool, Manager
import requests
import selenium.common.exceptions
from bs4 import BeautifulSoup
from tqdm import tqdm
from seleniumwire import webdriver


class PopularInformationFinder:
    """Finds the popular information amongst given sources

    Class that provides methods that get text from sources and compares the number of times a
    particular entity is mentioned.
    """

    def __init__(self, file_handler_object, entity_processor_object):
        """Initialises the PopularInformationFinder object.

        Args:
            file_handler_object: gives the class access to the file_handler object.
            entity_processor_object: gives the class access to the entity_processor object.
        """
        # Lazy creation of class attribute.
        try:
            manager = getattr(type(self), 'manager')
        except AttributeError:
            manager = type(self).manager = Manager()
        self.entities = manager.dict()
        self.file_handler = file_handler_object
        self.entity_processor = entity_processor_object

    def get_text_process_entities(self, source):
        """Gets the body text from each source using its URL.

        Uses requests and BeautifulSoup to retrieve and parse the webpage's HTML into a readable
        format for entity recognition.

        This method updates the 'self.sources' dictionary.

        Args:
            source: the individual source from the dictionary of sources.

        Returns:
            A list of key-value pairs (tuples).
            Note: key-value pairs are required for the map function to construct a dictionary from.
        """
        # define entities variable
        entities = []
        # define the url
        url = source["url"]
        # set headers to try to avoid 403 errors
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/112.0.0.0 Safari/537.36'}
        # request the webpage - if timeout, move on to next source
        try:
            response = requests.get(url, headers, timeout=5)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            return entities
        if "application/javascript" in response.headers['Content-Type'] \
                or response.status_code != 200:
            # using selenium to avoid 'JavaScript is not available." error
            options = webdriver.ChromeOptions()
            options.headless = True
            options.add_argument("start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                "like Gecko) Chrome/98.0.4758.102 Safari/537.36")
            try:
                service_log_path = "{}/chromedriver.log".format("/logs")
                service_args = ['--verbose']
                driver = webdriver.Chrome('chromedriver', chrome_options=options,
                                          service_args=service_args,
                                          service_log_path=service_log_path)
            except http.client.RemoteDisconnected:
                return entities
            driver.set_page_load_timeout(5)     # set timeout to 5 secs
            # request the webpage. If source website timeout, return the current list of entities.
            driver.get(url)
            html = driver.page_source
            # check if we are wasting our time with a broken or inaccessible website
            try:
                request = driver.wait_for_request(url, 5)
                response = request.response
                driver.quit()
            except selenium.common.exceptions.TimeoutException:
                driver.quit()
                return entities
            if request.response.status_code in {400, 401, 403, 404, 429}:
                driver.quit()
                return entities
        else:
            html = response.text
        # get the content type
        try:
            content_type = response.headers['Content-Type']
            # if xml use xml parser
            if content_type == "text/xml" or content_type == "application/xml":
                # don't parse xml
                return entities
            else:
                # parse using the lxml html parser
                soup = BeautifulSoup(html, "lxml")
        except KeyError:
            # except on KeyError if no 'content-type' header exists
            soup = BeautifulSoup(html, "lxml")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        # split into list
        textlist = text.split('\n')

        if len(text) <= 100000:
            # run the text through the entity processor. stores entities in namesake variable
            entities = self.entity_processor.get_entities_and_count(textlist, self.entities)
        return entities

    def find_entities(self, sources):
        """Finds entities in the given text.

        Uses the same model for entity recognition in specific_entity_processor.

        Looks like we need to scrap wikipedia articles because they are too long.
        Articles over 100k characters are probably too long also.
        Most slowdowns here have been due to Russia's wikipedia page.

        Args:
            sources: list of dictionaries of sources with corresponding URL.

        Returns:
            A list of the most popular words amongst all the sources.
        """
        with Pool() as pool:
            # sources = tqdm(sources)  # add a progress bar
            # calculate an even chunksize for the imap function using pool size (max processes)
            chunksize = len(sources) / len(pool._pool)
            if int(chunksize) < chunksize:
                chunksize = int(chunksize) + 1
            else:
                chunksize = int(chunksize)
            tmp = tqdm(pool.imap_unordered(self.get_text_process_entities, sources, chunksize),
                       total=len(sources), desc="Finding popular entities")
            self.entities.update([tpl for sublist in tmp for tpl in sublist if tpl])

        # sort list of dictionaries by highest no. of mentions.
        # lambda function specifies sorted to use the values of the dictionary in desc. order
        sorted_entities = sorted(self.entities.items(), key=lambda x: x[1], reverse=True)
        # keep top 10% of popular entities, and no greater than 30 entities.
        cut_off_index = len(sorted_entities) * 0.10
        cut_off_index = int(min(cut_off_index, 30))
        # truncate the list based on cut_off_index
        sorted_entities = itertools.islice(sorted_entities, cut_off_index)
        sorted_entities_words = list(word for (word, count) in sorted_entities)

        return sorted_entities_words
