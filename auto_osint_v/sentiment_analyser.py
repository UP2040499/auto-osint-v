"""This module's primary role is to analyse the semantics of the intelligence statement.

This module will likely be reused/modified within source aggregation.
"""

from transformers import pipeline


class SentimentAnalyser:
    """This class provides methods for conducting sentiment analysis on a given document.

    This document could be the intelligence statement or a different document.
    """

    def __init__(self, read_statement, statement_title, file_handler_object):
        """Initialises variables to be used in this object.

        Args:
            read_statement: This is the statement input in __main__.py and read by
                            FileHandler.read_file()
            statement_title: This is the source title or filename.
            file_handler_object: The file handler object passed to the class for reuse
        """
        self.statement = read_statement
        self.file_name = statement_title
        self.file_handler = file_handler_object
        # Trying a variety of models. Need one with 3 labels for +ve, -ve and neutral.
        # We want intelligence statements to be neutral and not too +ve or -ve
        self.sentiment_analysis = pipeline("sentiment-analysis",
                                           model="Souvikcmsa/BERT_sentiment_analysis")

    def set_statement(self, new_statement):
        """Setter for the self.statement initial variable"""
        self.statement = new_statement

    def statement_analyser(self):
        """This method analyses the overall sentiment of the intelligence statement.

        (it could be used to analyse other statements)
        This code is all from the Hugging Face documentation.

        Returns:
            Nothing - outputs to file
        """
        classification = self.sentiment_analysis(self.statement)
        # print(classification)
        # create a sentiment threshold for the intel statement
        # If the threshold is exceeded add extra information to warn user that their statement is
        # likely bias or sensational, see Calvo et al. (2021).
        threshold = 0.9
        # If you want a different threshold depending on source type,
        # add as a parameter to statement_analyser

        # Thought to offer better readability to user
        evidence_type = "sentiment-analysis-of-" + self.file_name
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

    def headline_analyser(self, headline):
        """Runs sentiment analysis on a given headline.

        Returns:
            the sentiment label (positive, negative, neutral) and the confidence score.
        """
        headline = headline.strip()
        classification = self.sentiment_analysis(headline)
        # get the label and score
        classification_label = classification[0]["label"]
        classification_score = classification[0]["score"]
        return classification_label, classification_score
