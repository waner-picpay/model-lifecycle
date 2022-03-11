""" Module containing the Document Adapter abstraction """
from abc import ABC, abstractmethod
from ast import Dict
from typing import List, Tuple


class IDocumentAdapter(ABC):
    """Class that abstracts file access on Amazon s3."""

    @abstractmethod
    def read(self, collection: str, match: dict) -> dict:
        """[summary]
        Args:
            collection (str): [description]
            key (str): [description]
            value (str): [description]
        Returns:
            dict: [description]
        """

    @abstractmethod
    def scan(self, collection) -> List:
        """[summary]
        Args:
            collection (str): [description]
        Returns:
            List: [description]
        """

    def query_custom(self, collection: str, query_dict: Dict) -> Tuple[List, Dict]:
        """_summary_

        Args:
            collection (str): _description_
            query_dict (Dict): _description_

        Returns:
            Tuple[List, Dict]: _description_
        """

    def query_custom_full(self, collection: str, query_dict: Dict=None) -> List:
            """_summary_

            Args:
                collection (str): _description_
                query_dict (Dict): _description_

            Returns:
                List: _description_
            """
