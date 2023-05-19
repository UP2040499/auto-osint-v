import csv
from unittest import TestCase
import os
from auto_osint_v.main import format_output
from auto_osint_v.file_handler import FileHandler


class Test(TestCase):
    @staticmethod
    def read_sources_file():
        with open("sources_test.csv", "r", encoding="utf-8") as sfile:
            reader = csv.DictReader(sfile)
            list_of_dicts = list(reader)
            return list_of_dicts

    def test_format_output(self):
        try:
            os.chdir("../unit_tests/")
            sources = self.read_sources_file()
        except FileNotFoundError as error:
            print(os.getcwd())
            print(error)
        os.chdir("../auto_osint_v/")
        data_file_path = os.getcwd() + "/data_files/"
        file_handler = FileHandler(data_file_path)
        out_df = format_output(sources, file_handler)
        # display the dataframe
        out_df.to_html(file_handler.get_output_path("", "html"))
