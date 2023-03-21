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
    def __init__(self, intel_statement, file_handler_object):
        """
        Initialises variables to be used in this object.
        :param intel_statement: This is the intelligence statement input in main.py
        """
        self.intel_statement = intel_statement
        self.file_handler = file_handler_object

    def statement_analyser(self):
        """
        This method analyses the intelligence statement.
        This code is all from the Hugging Face documentation.
        :return:
        """
        # Trying a variety of models. Need one with 3 labels for +ve, -ve and neutral.
        # We want intelligence statements to be neutral and not too +ve or -ve
        sentiment_analysis = pipeline("sentiment-analysis",
                                      model="Souvikcmsa/BERT_sentiment_analysis")
        classification = sentiment_analysis(self.intel_statement)
        print(classification)
        # create a sentiment threshold for the intel statement
        # If the threshold is exceeded add extra information to warn user that their statement is
        # likely bias or sensational, see Calvo et al. (2021).
        threshold = 0.9
        evidence_type = "semantic-analysis-of-statement"
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
