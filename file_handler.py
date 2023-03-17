"""
This module handles all our data files. CSV or TXT.
"""

import csv
import os
import webbrowser


class FileHandler:
    def __init__(self, data_file):
        self.data_file_path = data_file

    def write_bias_file(self):
        bias_file_path = str(os.path.join(self.data_file_path, "bias_sources.csv"))
        with open(bias_file_path, "w", encoding="utf-8") as bfile:
            fieldnames = ['Type', 'Key_Info']
            writer = csv.DictWriter(bfile, fieldnames)
            # enter source type and key information
            writer.writeheader()
            option = ""
            while option not in {"x", "X"}:
                source_type = str(input("Enter the source/intelligence type, "
                                        "for example HUMINT, SIGINT, etc.\n>>> "))
                key_info = str(input("Enter the key information proffered "
                                     "from this source/intelligence\n>>> "))
                writer.writerow({"Type": source_type, "Key_Info": key_info})
                option = str(input("Enter 'X' to finish entering sources. "
                                   "Press ENTER to add another source>>> "))
            bfile.close()

    def write_intel_file(self):
        intel_file_path = str(os.path.join(self.data_file_path, "intelligence_file.txt"))
        if os.path.isfile(intel_file_path):
            os.remove(intel_file_path)
        with open(intel_file_path, "x", encoding="utf-8") as fout:
            # Create file and close as will be edited in txt editor.
            statement_help = str("Intelligence statement help:\n"
                                 "- Please include as much information as possible.\n"
                                 "- Include known associates to the person(s) mentioned.\n"
                                 "- Remove this help section and replace it with your intelligence statement.\n"
                                 "- Be sure to save the file before continuing.")
            fout.write(statement_help)
            fout.close()
            webbrowser.open(intel_file_path)  # edit in chosen text editor

    def read_file(self, filename):
        file_path = str(os.path.join(self.data_file_path, filename))
        with open(file_path, "r", encoding="utf-8") as file:
            temp = file.read()
            file.close()
            return temp
