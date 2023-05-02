"""Unit test for the priority manager"""

import os
from unittest import TestCase
import pandas as pd
from auto_osint_v.file_handler import FileHandler
from auto_osint_v.priority_manager import PriorityManager


class TestPriorityManager(TestCase):
    """Unit test for the PriorityManager class"""
    def test_target_info_scorer(self):
        """Unit test for the target_info_scorer method"""
        fh_object = FileHandler(
            "..\\auto_osint_v\\data_files\\")
        pm_object = PriorityManager(fh_object)
        frame = pd.read_csv(os.getcwd() +
                            "/potential_corroboration_example.csv",
                            index_col=False)
        potential_corroboration = frame.to_dict("records")
        sources = pm_object.target_info_scorer(potential_corroboration)
        print([source["url"]["target_entity_count"] for source in sources])
