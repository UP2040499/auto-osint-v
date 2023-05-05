"""Unit test for the priority manager"""

import os
from unittest import TestCase
import pandas as pd
from auto_osint_v.file_handler import FileHandler
from auto_osint_v.specific_entity_processor import EntityProcessor
from auto_osint_v.priority_manager import PriorityManager


class TestPriorityManager(TestCase):
    """Provides test cases for the PriorityManager class"""
    def test_manager(self):
        """Unit test for the target_info_scorer method"""
        os.chdir("../unit_tests/")
        fh_object = FileHandler(
            "..\\auto_osint_v\\data_files\\")
        ep_object = EntityProcessor(fh_object)
        frame = pd.read_csv(os.getcwd() +
                            "/potential_corroboration_example.csv",
                            index_col=False)
        potential_corroboration = frame.to_dict("records")
        pm_object = PriorityManager(fh_object, ep_object, potential_corroboration)
        sources = pm_object.manager()
        print([f"url: {source['url']}, score: {source['score']}" for source in sources])

    def test_target_info_scorer(self):
        """Runs the 'target_info_scorer' in unit test"""
        fh_object = FileHandler(
            "..\\auto_osint_v\\data_files\\")
        ep_object = EntityProcessor(fh_object)
        os.chdir("../unit_tests/")
        frame = pd.read_csv(os.getcwd() +
                            "/potential_corroboration_example.csv",
                            index_col=False)
        potential_corroboration = frame.to_dict("records")
        pm_object = PriorityManager(fh_object, ep_object, potential_corroboration)
        pm_object.target_info_scorer()
        print(pm_object.get_sources())

    def test_popular_info_scorer(self):
        """Runs the 'popular_info_scorer' in unit test"""
        fh_object = FileHandler(
            "..\\auto_osint_v\\data_files\\")
        ep_object = EntityProcessor(fh_object)
        os.chdir("../unit_tests/")
        frame = pd.read_csv(os.getcwd() +
                            "/potential_corroboration_example2.csv",
                            index_col=False)
        potential_corroboration = frame.to_dict("records")
        pm_object = PriorityManager(fh_object, ep_object, potential_corroboration)
        pm_object.popular_info_scorer()
        print(pm_object.get_sources())
