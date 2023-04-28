"""This module assigns scores to each source, prioritising the most relevant sources.
"""

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


class PriorityManager:
    """Provides methods for assigning source scores based on relevancy to the user's statement.
    """

    def __init__(self, fh_object):
        """Initialises the PriorityManager object.

        Args:
            fh_object: file handler object to use for extracting info from data files.
        """
        self.target_entity_multiplier = 10
        self.file_handler = fh_object

    def get_text_from_site(self, url):
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
        # request the webpage
        response = requests.get(url, headers)
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

        return text

    def target_info_scorer(self, sources):
        """Assigns scores based on the amount of target entities identified.

        Args:
            sources: list of dictionaries of potential corroboration

        Returns:
            Returns the sources list of dictionaries, with an additional
            'target_entity_count' key-value pair.
        """
        # Gather saved target entities
        entities = self.file_handler.get_keywords_from_target_info()

        # Count number of appearances in each source
        for i, source in enumerate(tqdm(sources, desc="Counting target entity appearances in "
                                                      "sources")):
            # get the text from the source
            text = self.get_text_from_site(source["url"])
            # assign score based on entity appearance count
            score = self.count_entities(entities, text)*self.target_entity_multiplier
            # save score to the source dictionary
            source["target_entity_score"] = score
        # Return the updated 'sources' list of dictionaries
        return sources

    def count_entities(self, entities, source_text):
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
