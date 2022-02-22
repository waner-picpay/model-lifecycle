""" Module containing the Document Adapter abstraction """
from abc import ABC, abstractmethod
from typing import List


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