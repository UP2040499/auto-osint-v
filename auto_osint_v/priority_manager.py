"""This module assigns scores to each source, prioritising the most relevant sources.
"""

import requests
import multiprocessing
from tqdm import tqdm
from bs4 import BeautifulSoup
from auto_osint_v.popular_information_finder import PopularInformationFinder


class PriorityManager:
    """Provides methods for assigning source scores based on relevancy to the user's statement.
    """

    def __init__(self, fh_object, entity_processor_object, potential_corroboration):
        """Initialises the PriorityManager object.

        Args:
            fh_object: file handler object to use for extracting info from data files.
            entity_processor_object: object to use for processing entities
            potential_corroboration: list of dictionaries of source information.
        """
        self._target_entity_multiplier = 10  # multiplier for mentions of target info
        self._popular_entity_multiplier = 5  # multiplier for mentions of popular info
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
        # generate a popular info score for each source
        self.popular_info_scorer()
        # sort sources by score in descending order
        self.sort_sources_desc()
        # return scored sources list(dict)
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
        except requests.exceptions.ReadTimeout:
            return text
        # check if we are wasting our time with a broken or inaccessible website
        try:
            response.raise_for_status()
        except requests.HTTPError:
            return text
        # get the html from the response
        html = response.text
        # parse HTML using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
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

        Updates the 'self.sources' public variable
        """
        # Gather saved target entities
        entities = self.file_handler.get_keywords_from_target_info()

        # Count number of appearances in each source
        for source in tqdm(self.sources, desc="Counting target entity appearances in "
                                              "sources"):
            # get the text from the source
            text = self.get_text_from_site(source["url"])
            # assign score based on entity appearance count
            score = self.count_entities(entities, text) * self._target_entity_multiplier
            # adds score to the source dictionary
            try:
                source["score"] += score
            except KeyError:
                source["score"] = score
        # Updated 'self.sources' list of dictionaries

    def popular_info_scorer(self):
        """Assigns scores to each source based on the amount of popular entities identified"""
        # initialise popular info finder object
        popular_ent_finder = PopularInformationFinder(self.file_handler, self.entity_processor)
        # Gather popular entities
        entities = popular_ent_finder.find_entities(self.sources)
        # Count number of appearances in each source
        #for source in tqdm(self.sources, desc="Counting popular entity appearances in "
        #                                      "sources"):
        #    self.get_text_assign_score(entities, source)
        # new approach using multiprocessing map function
        with multiprocessing.Pool() as p:
            self.sources = list(p.map(self.get_text_assign_score, entities, self.sources))
        # Updated 'self.sources' list of dictionaries

    def get_text_assign_score(self, entities, source):
        # get the text from the source
        text = self.get_text_from_site(source["url"])
        # assign score based on entity appearance count
        score = self.count_entities(entities, text) * self._popular_entity_multiplier
        # adds score to the source dictionary
        try:
            source["score"] += score
        except KeyError:
            source["score"] = score
        return source

    @staticmethod
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

    def remove_sources(self):
        """Removes sources that have a score of 0."""
        self.sources = [dict_ for dict_ in self.sources if dict_["score"] != 0]

    def sort_sources_desc(self):
        """Sorts the 'self.sources' list of dicts in descending order based on score."""
        # sort sources list of dictionaries by highest score.
        # lambda function specifies sorted to use the values of the dictionary in desc. order
        self.sources = sorted(self.sources.items(), key=lambda x: x["score"], reverse=True)
