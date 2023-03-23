"""
This module's primary role is to analyse the semantics of the intelligence statement.
This module will likely be reused/modified within source aggregation.
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

import file_handler


class SemanticAnalyser:
    """
    This class provides methods for conducting semantic analysis on a given document.
    This document could be the intelligence statement or a different document.
    """
    def __init__(self, read_statement, statement_title, file_handler_object):
        """
        Initialises variables to be used in this object.
        :param read_statement: This is the statement input in main.py and read by
        FileHandler.read_file()
        :param statement_title: This is the source title or filename.
        :param file_handler_object: The file handler object passed to the class for reuse
        """
        self.statement = read_statement
        self.file_name = statement_title
        self.file_handler = file_handler_object

    def statement_analyser(self):
        """
        This method analyses the intelligence statement.
        (or it may be used to analyse other statements)
        This code is all from the Hugging Face documentation.
        :return:
        """
        # Trying a variety of models. Need one with 3 labels for +ve, -ve and neutral.
        # We want intelligence statements to be neutral and not too +ve or -ve
        sentiment_analysis = pipeline("sentiment-analysis",
                                      model="Souvikcmsa/BERT_sentiment_analysis")
        classification = sentiment_analysis(self.statement)
        # print(classification)
        # create a sentiment threshold for the intel statement
        # If the threshold is exceeded add extra information to warn user that their statement is
        # likely bias or sensational, see Calvo et al. (2021).
        threshold = 0.9
        # If you want a different threshold depending on source type,
        # add as a parameter to statement_analyser

        # Thought to offer better readability to user
        evidence_type = "semantic-analysis-of-"+self.file_name
        classification_label = classification[0]["label"]
        classification_score = classification[0]["score"]
        if classification_label != 'neutral' and classification_score > threshold:
            # write analysis info and a warning as extra info
            warning = ("Warning: analysis of your statement indicates it is likely biased or "
                       "sensational")
            self.file_handler.open_evidence_file([evidence_type, classification_label +
                                                  ' sentiment, score: ' + str(classification_score),
                                                  warning])
        else:
            # write just the analysis info
            self.file_handler.open_evidence_file([evidence_type, classification_label +
                                                  ' sentiment, score: ' + str(classification_score)]
                                                 )
