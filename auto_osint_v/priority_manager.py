"""This module assigns scores to each source, prioritising the most relevant sources.
"""
import http.client
import inspect
import multiprocessing
from os import getpid
from typing import List
from multiprocessing import Pool
import requests
import selenium.common.exceptions
from tqdm import tqdm
from bs4 import BeautifulSoup
from seleniumwire import webdriver


from auto_osint_v.popular_information_finder import PopularInformationFinder


def count_entities(entities, source_text):
    """Counts the number of entities appearing in a given source.

    Args:
        entities: the entities to look for.
        source_text: the source text to look for entities within.

    Returns:
        Integer number of appearances of all entities in the source
    """
    entity_count = 0
    for entity in entities:
        # built-in method find() returns the index of a given substring within
        # a string, returns -1 if not found
        if source_text.find(entity) != -1:
            entity_count += 1
    return entity_count


class PriorityManager:
    """Provides methods for assigning source scores based on relevancy to the user's statement.
    """

    def __init__(self, fh_object, entity_processor_object, potential_corroboration: List[dict]):
        """Initialises the PriorityManager object.

        Args:
            fh_object: file handler object to use for extracting info from data files.
            entity_processor_object: object to use for processing entities
            potential_corroboration: list of dictionaries of source information.
        """
        self._target_entity_multiplier = 10  # multiplier for mentions of target info
        self._popular_entity_multiplier = 5  # multiplier for mentions of popular info
        self._entities = []
        self.file_handler = fh_object
        self.entity_processor = entity_processor_object
        self.sources = potential_corroboration

    def manager(self):
        """This method controls the order of execution for counting target and popular info.

        Returns:
            self.sources: list of dictionaries of source information
        """
        self.target_info_scorer()  # generates a score for each source
        # remove sources with 0 score (or could remove bottom x% of sources)
        self.remove_sources()
        # clear entities list
        self._entities.clear()
        # generate a popular info score for each source
        self.popular_info_scorer()
        # sort sources by score in descending order
        self.sort_sources_desc()
        # return scored sources list(dict)
        return self.sources

    def get_sources(self):
        """Method for getting the list of source dictionaries."""
        return self.sources

    @staticmethod
    def get_text_from_site(url):
        """Gets the body text from each source using its URL.

        Uses requests and BeautifulSoup to retrieve and parse the webpage's HTML into a readable
        format for entity recognition.

        Args:
            url: url fetched from sources dictionary.

        Returns:
            The content of the webpage in UTF-8 format.
        """
        # initialise the webpage text variable
        text = ""
        # set headers to try to avoid 403 errors
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/112.0.0.0 Safari/537.36'}
        # request the webpage - if timeout, move on to next source
        try:
            response = requests.get(url, headers, timeout=5)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            return text
        try:
            content_type = response.headers['Content-Type']
        except KeyError:
            content_type = ''
        if "application/javascript" in content_type \
                or response.status_code != 200:
            # using selenium to avoid 'JavaScript is not available' error
            options = webdriver.ChromeOptions()
            options.headless = True
            options.add_argument("--no-sandbox")
            options.add_argument("start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                "like Gecko) Chrome/98.0.4758.102 Safari/537.36")
            try:
                driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
            except http.client.RemoteDisconnected:
                driver.quit()
                return text
            # driver.set_page_load_timeout(5)  # set timeout to 5 secs
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
                return text
            if request.response.status_code in {400, 401, 403, 404, 429}:
                driver.quit()
                return text
        else:
            html = response.text
        # get the content type
        try:
            # response is either the requests or selenium response
            content_type = response.headers['Content-Type']
            # if xml use xml parser
            if content_type == "text/xml" or content_type == "application/xml":
                # don't parse xml
                return text
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
        # return string text formatted and with line breaks
        return text

    def target_info_scorer(self):
        """Assigns scores based on the amount of target entities identified.

        Updates the 'self.sources' list of dicts
        """
        # Gather saved target entities
        self._entities = self.file_handler.get_keywords_from_target_info()

        # Count number of appearances in each source
        # for source in tqdm(self.sources, desc="Counting target entity appearances in "
        #                                      "sources"):
        print(f"I am the parent, with PID {getpid()}")
        with multiprocessing.get_context('spawn').Pool() as pool:
            self.sources = list(tqdm(pool.imap_unordered(self.get_text_get_score_target_inf,
                                                         self.sources), total=len(self.sources),
                                     desc="Assigning scores to sources based on target info"))
        # Updated 'self.sources' list of dictionaries

    def popular_info_scorer(self):
        """Assigns scores to each source based on the amount of popular entities identified.

        Updates the 'self.sources' list of dicts.
        """
        # initialise popular info finder object
        popular_info_object = PopularInformationFinder(self.file_handler, self.entity_processor)
        # Gather popular entities
        entities = popular_info_object.find_entities(self.sources)
        self._entities = entities
        # Count number of appearances in each source
        # new approach using multiprocessing map function
        with multiprocessing.get_context('spawn').Pool() as pool:
            self.sources = list(tqdm(pool.imap_unordered(self.get_text_get_score_pop_inf,
                                                         self.sources), total=len(self.sources),
                                     desc="Assigning scores to sources based on popular info"))
        # Updated 'self.sources' list of dictionaries

    def get_text_get_score_target_inf(self, source):
        """Gets the text from the source URL and assigns a score.

        Args:
            source: the individual source dictionary of information

        Returns:
            the updated source dictionary with a new 'score' field.
        """
        print(f"I am the child, with PID {getpid()}")
        # get the text from the source
        text = self.get_text_from_site(source["url"])
        # return score for target info
        score = int(count_entities(self._entities, text) * self._target_entity_multiplier)
        # adds score to the source dictionary
        try:
            source["score"] += score
        except KeyError:
            source["score"] = score
        return source

    def get_text_get_score_pop_inf(self, source):
        """Gets the text from the source URL and assigns a score.

        Args:
            source: the individual source dictionary of information

        Returns:
            the updated source dictionary with a new 'score' field.
        """
        # get the text from the source
        text = self.get_text_from_site(source["url"])
        # return score for target info
        score = int(count_entities(self._entities, text) * self._target_entity_multiplier)
        # adds score to the source dictionary
        try:
            source["score"] += score
        except KeyError:
            source["score"] = score
        return source

    def get_text_assign_score(self, source):
        """Gets the text from the source URL and examines it to count the number of entities.

        Args:
            source: the individual source dictionary of information.
        """
        # get the text from the source
        text = self.get_text_from_site(source["url"])
        # assign score based on entity appearance count
        # use different multiplier depending on which method has called 'get_text_assign_score()'
        if inspect.stack()[1].function == "target_info_scorer()":
            score = count_entities(self._entities, text) * self._target_entity_multiplier
        elif inspect.stack()[1].function == "popular_info_scorer()":
            score = count_entities(self._entities, text) * self._popular_entity_multiplier
        else:
            score = 10
        # adds score to the source dictionary
        try:
            source["score"] += score
        except KeyError:
            source["score"] = score
        return source

    def remove_sources(self):
        """Removes sources that have a score of 0."""
        self.sources = [dict_ for dict_ in self.sources if dict_["score"] != 0]

    def sort_sources_desc(self):
        """Sorts the 'self.sources' list of dicts in descending order based on score."""
        # sort sources list of dictionaries by highest score.
        # lambda function specifies sorted to use the values of the dictionary in desc. order
        self.sources.sort(key=lambda x: x["score"], reverse=True)
