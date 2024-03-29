"""This module handles all our data files. CSV or TXT.
"""

import csv
import os
import webbrowser
import pandas as pd


class FileHandler:
    """FileHandler class handles anything file related for the whole tool.

    This can be created as an object once and reused multiple times.
    """
    def __init__(self, data_file):
        """Initialises the FileHandler object

        Args:
            data_file: the file path for all data files - likely './data_files/'.
        """
        # empty list to hold unique urls present after searching
        self.urls_present = []
        self.data_file_path = data_file

    def write_bias_file(self, info_analyser):
        """Creates and writes to the bias information file.

        This bias information is only useful for the user if they want to include information that
        the tool cannot use, but may be relevant to their analysis or conclusions.

        Returns:
            nothing - output to file
        """
        bias_file_path = str(os.path.join(self.data_file_path, "bias_sources.csv"))
        with open(bias_file_path, "w", encoding="utf-8") as bfile:
            fieldnames = ['Type/Link', 'Key Info', 'Info Sentiment']
            writer = csv.DictWriter(bfile, fieldnames)
            # enter source type and key information
            writer.writeheader()
            option = ""
            while option not in {"x", "X"}:
                source_type = str(input("If you wish to enter a source that has no URL, just enter "
                                        "the type of source (e.g. HUMINT, SIGINT, etc.)."
                                        "If it is an open source, please enter the URL.\n>>> "))
                key_info = str(input("Enter the key information proffered "
                                     "from this source/intelligence\n>>> "))
                writer.writerow({"Type/Link": source_type, "Key Info": key_info,
                                 "Info Sentiment": info_analyser(key_info)})
                option = str(input("Enter 'X' to finish entering sources. "
                                   "Press ENTER to add another source>>> "))
            bfile.close()

    def read_bias_file(self):
        bias_file_path = str(os.path.join(self.data_file_path, "bias_sources.csv"))
        with open(bias_file_path, "r", encoding="utf-8") as bfile:
            reader = csv.DictReader(bfile)
            list_of_dicts = list(reader)
            return list_of_dicts

    def write_intel_file(self, editor: bool):
        """Creates and writes a file for the intelligence statement to be stored in.

        This opens the file in the text editor for easier statement writing.

        Returns:
            nothing - output to file
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
            if editor:
                fout.write(statement_help)
                fout.close()
                webbrowser.open(intel_file_path)  # edit in default text editor
            else:
                statement = str(input(statement_help))
                fout.write(statement)
                fout.close()

    def read_file(self, filename):
        """Reads the given file. Reads any file, extension is included in filename.

        Args:
            filename: includes the file extension.

        Returns:
            the contents of the file
        """
        file_path = str(os.path.join(self.data_file_path, filename))
        with open(file_path, "r", encoding="utf-8") as file:
            temp = file.read()
            file.close()
            return temp

    def get_keywords_from_target_info(self):
        """Gets all the information that is stored in the 'Info' field in each target info file.

        Returns:
            All the info stored in /target_info_files/
        """
        # List of words that have no meaning without context
        irrelevant_words = ["it", "them", "they", "the", "he", "she", "his", "her", "we", "i",
                            "us", "me", "my", "here", "our"]
        # the directory to find the target info files
        target_files_dir = os.path.join(self.data_file_path, "target_info_files/")
        # list target info files
        target_files = os.listdir(target_files_dir)
        # Create list to store keywords
        info_all = []
        # read each file individually
        for file in target_files:
            filepath = os.path.join(target_files_dir, file)
            frame = pd.read_csv(filepath, index_col=False)
            # appends every entry in the 'info' column to the 'info_all' list unless
            # it is irrelevant
            values = frame["Info"].values.tolist()
            info_all.extend(values)
        # remove irrelevant words
        info_all = [word for word in info_all if word not in irrelevant_words]
        # return list after each file has been examined
        return info_all

    @staticmethod
    def clean_directory(directory):
        """Cleans the given directory. Removes all files inside.
        """
        try:
            for file in os.listdir(directory):
                os.remove(os.path.join(directory, file))
        except FileNotFoundError:
            pass

    def clean_data_file(self, filename):
        """Removes all data in given file

        Args:
            filename: name of file, can be path relative to 'data_files' directory
        """
        try:
            os.remove(os.path.join(self.data_file_path, filename))
        except FileNotFoundError:
            pass

    @staticmethod
    def write_to_given_csv_file(file_object, to_write):
        """Writes given text to a given file object.

        Args:
            to_write: iterable to write to the csv file
            file_object: the file object, created when opening a file
                (e.g., "with open(file) as file_object:")

        Returns:
            Nothing
        """
        try:
            writer = csv.writer(file_object, delimiter=',')
            writer.writerow(to_write)  # writes a row of the csv file using the list 'to_files'
        except ValueError as exc:
            raise ValueError(
                "I/O operation on closed file. Issue with FileHandler.open_label_file") \
                from exc

    def write_to_txt_file_remove_duplicates(self, file_object, to_write):
        """Writes the given text and ensures no duplicates are written.

        Args:
            file_object: File object passed from opening the file.
            to_write: The text to write.
        """
        # check whether lines are unique
        if to_write not in self.urls_present:
            # write to file
            file_object.write(to_write + "\n")
            # add unique line to lines_present lines
            self.urls_present.append(to_write)

    def open_txt_file(self, filename):
        """Opens a file or creates one if it does not exist, returns the fileIO object.

        Clean every temp file created here by using clean_directory.

        Args:
            filename: name of file to open

        Returns:
            file object
        """
        try:
            return open(os.path.join(self.data_file_path, filename), "a", encoding="utf-8")
        except FileNotFoundError:
            return open(os.path.join(self.data_file_path, filename), "w", encoding="utf-8")

    @staticmethod
    def close_file(file_object):
        """Closes a given file.

        Args:
            file_object: The file object for the file to be closed

        Returns:
            nothing, just closes a file.
        """
        file_object.close()

    def open_label_file(self, label, text, mentions):
        """Creates/Opens label file directory and the label file itself.

        Args:
            text: The labelled word
            mentions: The number of times the text has appeared.
            label: This will be the name for the label file. This is the label associated with a
                word

        Returns:
            Nothing - output to file
        """
        label_files_directory = self.data_file_path + "target_info_files"
        try:
            os.mkdir(label_files_directory)
            file_path = str(os.path.join(label_files_directory, label + ".csv"))
        except FileExistsError:
            file_path = str(os.path.join(label_files_directory, label + ".csv"))
        fieldnames = ['Info', 'Mentions']
        try:
            with open(file_path, "x", encoding="utf-8") as label_file:
                # Creation of csv file
                writer = csv.DictWriter(label_file, fieldnames)
                # enter source type and key information
                writer.writeheader()
                # Write info to csv
                to_write = [text, mentions]
                self.write_to_given_csv_file(label_file, to_write)
        except FileExistsError:
            with open(file_path, "a", encoding="utf-8") as label_file:
                # Write info to csv
                to_write = [text, mentions]
                self.write_to_given_csv_file(label_file, to_write)

    def open_evidence_file(self, to_write):
        """Creates/Opens evidence file and writes to it.

        Args:
            to_write: List of elements to write to file

        Returns:
            Nothing - output to file
        """
        evidence_file_path = self.data_file_path + "evidence_file.csv"
        fieldnames = ["evidence type", "info", "extra info", "score", "source link"]
        try:
            with open(evidence_file_path, "x", encoding="utf-8") as evidence_file:
                # Creation of csv file
                writer = csv.DictWriter(evidence_file, fieldnames)
                writer.writeheader()
                # Write info to csv
                self.write_to_given_csv_file(evidence_file, to_write)
        except FileExistsError:
            with open(evidence_file_path, "a", encoding="utf-8") as evidence_file:
                # Append info to csv
                self.write_to_given_csv_file(evidence_file, to_write)

    def read_evidence_file(self):
        evidence_file_path = self.data_file_path + "evidence_file.csv"
        with open(evidence_file_path, "r", encoding="utf-8") as evidence_file:
            reader = csv.DictReader(evidence_file)
            list_of_dicts = list(reader)
            return list_of_dicts

    def create_potential_corroboration_file(self, sources_list_of_dicts):
        """Creates the potential corroboration source store.

        Writes the list of dictionaries to a csv file.

        Args:
            sources_list_of_dicts: Must be a list of dictionaries ( list[dict[x,y]] )

        Returns:
            nothing, outputs to file
        """
        sources_file_path = self.data_file_path + "potential_corroboration.csv"
        try:
            self.clean_data_file("potential_corroboration.csv")
        except FileNotFoundError:
            pass
        # get keys of dictionary and store as fieldnames
        fieldnames = sources_list_of_dicts[0].keys()
        with open(sources_file_path, "x", newline="", encoding="utf-8") as sources_file:
            # create writer object
            writer = csv.DictWriter(sources_file, fieldnames)
            writer.writeheader()
            # write the dictionary to csv
            writer.writerows(sources_list_of_dicts)

    def get_output_path(self, postfix, file_ext):
        """Gets the path of the output file"""
        output_directory = self.data_file_path + "output"
        try:
            os.mkdir(output_directory)
            file_path = str(os.path.join(output_directory, f"output{postfix}.{file_ext}"))
        except FileExistsError:
            file_path = str(os.path.join(output_directory, f"output{postfix}.{file_ext}"))
        return file_path
