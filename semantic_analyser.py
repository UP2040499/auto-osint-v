"""
This module's primary role is to analyse the semantics of the intelligence statement.
This module will likely be reused/modified within source aggregation.
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline


class SemanticAnalyser:
    """
    This class provides methods for conducting semantic analysis on a given document.
    This document could be the intelligence statement or a different document.
    """
    def __init__(self, intel_statement):
        """
        Initialises variables to be used in this object.
        :param intel_statement: This is the intelligence statement input in main.py
        """
        self.intel_statement = intel_statement

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
        print(sentiment_analysis(self.intel_statement))
        # create a sentiment threshold for the intel statement
        # If the threshold is exceeded add extra information to warn user that their statement is
        # likely bias or sensational, see Calvo et al. (2021).
