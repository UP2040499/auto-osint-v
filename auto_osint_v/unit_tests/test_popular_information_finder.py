from unittest import TestCase

import os
import pandas as pd


class TestPopularInformationFinder(TestCase):
    def test_find_entities(self):
        os.chdir('C:\\Users\\petec\\OneDrive\\Documents\\UniWork\\Year3\\FYP\\auto-osint-v'
                 '\\auto_osint_v\\')
        from auto_osint_v.file_handler import FileHandler
        from auto_osint_v.specific_entity_processor import EntityProcessor
        fh_object = FileHandler(
            "C:\\Users\\petec\\OneDrive\\Documents\\UniWork\\Year3\\FYP\\auto-osint-v"
            "\\auto_osint_v\\data_files\\")
        ep_object = EntityProcessor(fh_object)
        from auto_osint_v.popular_information_finder import PopularInformationFinder
        pif_object = PopularInformationFinder(fh_object, ep_object)
        """Original test data
        potential_corroboration = [{"url": "https://www.cnn.com/2022/02/24/europe/ukraine-russia"
                                           "-attack-timeline-intl/index.html"},
                                   {"url": "https://www.bbc.com/news/world-europe-56720589"},
                                   {"url": "https://www.pbs.org/newshour/world/1-year-after-the"
                                           "-invasion-began-a-timeline-of-russias-war-in-ukraine"},
                                   {"url": "https://acleddata.com/2023/03/20/ukraine-crisis-4-10"
                                           "-march-2023/"}]
        """
        frame = pd.read_csv(os.getcwd() +
                            "/unit_tests/potential_corroboration_example2.csv",
                            index_col=False)
        potential_corroboration = frame.to_dict("records")
        print(pif_object.find_entities(potential_corroboration))
