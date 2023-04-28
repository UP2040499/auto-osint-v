"""
Finds entities (information) that is popular amongst the potentially corroborating sources.
"""
import requests
import itertools
from bs4 import BeautifulSoup
from tqdm import tqdm


class PopularInformationFinder:
    """
    Class that provides methods that get text from sources and compares the number of times a
    particular entity is mentioned.
    """

    def __init__(self, file_handler_object, entity_processor_object):
        """

        Args:
            file_handler_object: gives the class access to the file_handler object.
            entity_processor_object: gives the class access to the entity_processor object.

        Returns:

        """
        self.file_handler = file_handler_object
        self.entity_processor = entity_processor_object

    def get_text_process_entities(self, url, entities):
        """Gets the body text from each source using its URL.

        Uses requests and BeautifulSoup to retrieve and parse the webpage's HTML into a readable
        format for entity recognition.

        Args:
            entities: the dictionary of entities.
            url: url fetched from sources dictionary.

        Returns:
            The content of the webpage in UTF-8 format.
        """
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
            return entities
        # get the html from the response
        html = response.text
        # parse HTML using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()

        # this doesn't work getting random webpage bits in the entities
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        if len(text) <= 100000:
            # run the text through the entity processor. stores entities in namesake variable
            entities = self.entity_processor.get_entities_and_count(text, entities)
        # else print/save source that has been skipped

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
        entities = {}

        for i, source in enumerate(tqdm(sources, desc="Getting text and finding entities")):
            # get the text from each source and find the entities
            entities = self.get_text_process_entities(source["url"], entities)

        # entities = dict(map(self.get_text_process_entities, sources, entities))

        # sort dictionary by highest no. of mentions.
        # lambda function specifies sorted to use the values of the dictionary in desc. order
        sorted_entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)
        # keep top 2.5% of words - this is an arbitrary value, not sure what value is best.
        # using itertools to slice the dictionary
        cut_off_value = int(len(sorted_entities) * 0.025)
        sorted_entities = itertools.islice(sorted_entities, cut_off_value)
        # return the list of words
        sorted_entities_words = list(word for (word, count) in sorted_entities)

        return sorted_entities_words
