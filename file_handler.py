"""
This module handles all our data files. CSV or TXT.
"""

import csv
import os
import webbrowser


def write_to_csv_file(file_object, text, alias):
    """
    Writes given text to a given file object.
    :param alias: can be empty string. useful for info
    such as coordinates to give an alias (location name) to them.
    :param text: the given text to
    write to the file.
    :param file_object: the file object, created when opening a file (e.g.,
    "with open(file) as file_object:")
    :return: Nothing
    """
    try:
        fieldnames = ['Info', 'Alias']
        writer = csv.DictWriter(file_object, fieldnames)
        writer.writerow({'Info': text, 'Alias': alias})
    except ValueError as exc:
        raise ValueError("I/O operation on closed file. Issue with FileHandler.open_label_file") \
            from exc


class FileHandler:
    """
    FileHandler class handles anything file related for the whole tool.
    This can be created as an object once and reused multiple times.
    """
    def __init__(self, data_file):
        """
        Initialises the FileHandler object
        :param data_file: the file path for all data files - likely './data_files/'.
        """
        self.data_file_path = data_file

    def write_bias_file(self):
        """
        Creates and writes to the bias information file.
        This bias information is only useful for the user if they want to include information that
        the tool cannot use, but may be relevant to their analysis or conclusions.
        :return: nothing - output to file
        """
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
        """
        Creates and writes a file for the intelligence statement to be stored in.
        This opens the file in the text editor for easier statement writing.
        :return: nothing - output to file
        """
        intel_file_path = str(os.path.join(self.data_file_path, "intelligence_file.txt"))
        if os.path.isfile(intel_file_path):
            os.remove(intel_file_path)
        with open(intel_file_path, "x", encoding="utf-8") as fout:
            # Create file and close as will be edited in txt editor.
            statement_help = str("Intelligence statement help:\n"
                                 "- Please include as much information as possible.\n"
                                 "- Include known associates to the person(s) mentioned.\n"
                                 "- Remove this help section and replace it with your "
                                 "intelligence statement.\n"
                                 "- Be sure to save the file before continuing.")
            fout.write(statement_help)
            fout.close()
            webbrowser.open(intel_file_path)  # edit in chosen text editor

    def read_file(self, filename):
        """
        Reads the given file. Reads any file, extension is included in filename.
        :param filename: includes the file extension.
        :return: the contents of the file
        """
        file_path = str(os.path.join(self.data_file_path, filename))
        with open(file_path, "r", encoding="utf-8") as file:
            temp = file.read()
            file.close()
            return temp

    @staticmethod
    def clean_directory(directory):
        """
        Cleans the given directory. Removes all files inside.
        :return:
        """
        for file in os.listdir(directory):
            os.remove(os.path.join(directory, file))

    def open_label_file(self, label, text, alias):
        """
        Creates/Opens label file directory and the label file itself
        :param text: The labelled word
        :param alias: An alias for the information labelled.
        :param label: This will be the name for the label file. This is the label associated with a
        word
        :return: Nothing - output to file
        """
        label_files_directory = self.data_file_path + "target_info_files"
        try:
            os.mkdir(label_files_directory)
            file_path = str(os.path.join(label_files_directory, label + ".csv"))
        except FileExistsError:
            file_path = str(os.path.join(label_files_directory, label + ".csv"))
        try:
            with open(file_path, "x", encoding="utf-8") as label_file:
                # Creation of csv file
                fieldnames = ['Info', 'Alias']
                writer = csv.DictWriter(label_file, fieldnames)
                # enter source type and key information
                writer.writeheader()
                # Write info to csv
                write_to_csv_file(label_file, text, alias)
        except FileExistsError:
            with open(file_path, "a", encoding="utf-8") as label_file:
                # Write info to csv
                write_to_csv_file(label_file, text, alias)
