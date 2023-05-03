"""Unit test for the popular information finder class."""
from unittest import TestCase
import os
import pandas as pd
from auto_osint_v.file_handler import FileHandler
from auto_osint_v.specific_entity_processor import EntityProcessor
from auto_osint_v.popular_information_finder import PopularInformationFinder


class TestPopularInformationFinder(TestCase):
    def test_find_entities(self):
        fh_object = FileHandler(
            "..\\auto_osint_v\\data_files\\")
        ep_object = EntityProcessor(fh_object)
        pif_object = PopularInformationFinder(fh_object, ep_object)
        os.chdir("../unit_tests/")
        frame = pd.read_csv(os.getcwd() +
                            "/potential_corroboration_example2.csv",
                            index_col=False)
        potential_corroboration = frame.to_dict("records")
        print(pif_object.find_entities(potential_corroboration))
