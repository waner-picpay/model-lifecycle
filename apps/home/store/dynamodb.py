""" Module containing the Dynamo DB Adapter implementation """
from typing import Dict, List, Tuple

from boto3.dynamodb.conditions import Key
from boto3.session import Session  # type: ignore
from botocore.exceptions import ClientError
from store.interfaces import IDocumentAdapter

from factories.logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)

ERROR_HELP_STRINGS = {
    # Common Errors
    "InternalServerError": "Internal Server Error, generally safe to retry with exponential back-off",
    "ProvisionedThroughputExceededException": "Request rate is too high. If you're using a custom retry strategy make sure to retry with exponential back-off."
    + "Otherwise consider reducing frequency of requests or increasing provisioned capacity for your table or secondary index",
    "ResourceNotFoundException": "One of the tables was not found, verify table exists before retrying",
    "ServiceUnavailable": "Had trouble reaching DynamoDB. generally safe to retry with exponential back-off",
    "ThrottlingException": "Request denied due to throttling, generally safe to retry with exponential back-off",
    "UnrecognizedClientException": "The request signature is incorrect most likely due to an invalid AWS access key ID or secret key, fix before retrying",
    "ValidationException": "The input fails to satisfy the constraints specified by DynamoDB, fix input before retrying",
    "RequestLimitExceeded": "Throughput exceeds the current throughput limit for your account, increase account level throughput before retrying",
}


class DynamoAdapter(IDocumentAdapter):
    """Class that abstracts file access on Amazon s3."""

    def __init__(self, session: Session):
        """Creates a s3FileAdapter by wrapping boto3 Session.
        Args:
            session (Session): An instance of boto3 Session.
        """
        self._session = session
        self._database = session.resource("dynamodb")

    def read(self, collection: str, match: dict) -> Dict:
        """Get an Item on Drynamodb
        Args:
            collection (str): The collection or table name
            match (dict): The key to be searched
        Returns:
            dict: Returns the found content
        Example:
            >>> dynamo_db.read('collection_name', {'consumer_id':1234})
        """

        table = self._database.Table(collection)

        item = table.get_item(Key=match).get("Item")

        return item

    def scan(self, collection, offset: None, limit=20) -> Tuple[List, Dict]:

        table = self._database.Table(collection)
        if offset is None:
            response = table.scan(Limit=limit)
        else:
            response = table.scan(ExclusiveStartKey=offset, Limit=limit)

        data = response["Items"]
        return (
            data,
            response["LastEvaluatedKey"] if "LastEvaluatedKey" in response else None,
        )

    @staticmethod
    def handle_error(error):
        error_code = error.response["Error"]["Code"]
        error_message = error.response["Error"]["Message"]

        error_help_string = ERROR_HELP_STRINGS[error_code]

        logger.error(
            "[{error_code}] {help_string}. Error message: {error_message}".format(
                error_code=error_code,
                help_string=error_help_string,
                error_message=error_message,
            )
        )

    def query_custom(self, collection: str, query_dict: Dict) -> Tuple[List, Dict]:
        try:
            response = self._database.Table(collection).query(**query_dict)
            data = response["Items"]
            return (
                data,
                response["LastEvaluatedKey"]
                if "LastEvaluatedKey" in response
                else None,
            )

        except ClientError as error:
            DynamoAdapter.handle_error(error)
        except BaseException as error:
            logger.error(f"Unknown error while executing query: {error}")