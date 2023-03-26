"""
Python Class for all functions of aggregating sources from open sources.
This includes using search engines (Google) and searching social media websites
(Twitter, Reddit, etc.)
"""


class SourceAggregator:
    """
    Provides methods for aggregating sources (see docstring).
    Most methods here will be private - not accessible by the rest of the program.
    This is because I want the aggregator to do all its work in one 'box' - likely more reusable as
    it can be shipped as a class with one input & one output.
    Everything output will be put into a 'Potential Corroboration Store'.
    """
    # Initialise object
    def __init__(self, intel_statement):
        self.intel_statement = intel_statement

    # For searching, I think the key information needs to be extracted from the intel statement
    # Don't want to search using just the intel statement itself.
    # Google Search

    # Social Media Search

    # Video Processor

    # Source Similarity Check
    # Very poor scores will lead to the source being discarded

    # Key information generator (likely using BERT QA)
    # Should try to make reusable (key info from statement and key info from sources)

    # Semantic analysis of key information and headlines
    # Very poor scores will lead to the source being discarded
    # Finally, store all potentially corroborating sources.

    # Will need a 'find_sources' method that runs all methods in this class. This method will
    # interface with the rest of the program.
