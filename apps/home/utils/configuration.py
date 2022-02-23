import os
from typing import Any

from boto3.session import Session

from apps.home.factories.session import Boto3SessionFactory
from apps.home.factories.logger import LoggerFactory
from apps.home.store.dynamodb import DynamoAdapter
from apps.home.store.interfaces import IDocumentAdapter

logger = LoggerFactory.get_logger(__name__)


class Configuration:
    """Class that abstracts parameter store and sessions on Amazon aws."""

    def __init__(
        self,
        session: Session = None,
        document_adapter: IDocumentAdapter = None,
        environment: str = None,
    ):

        self._session = session if session else Boto3SessionFactory.get_or_create()

        self._document_adapter = (
            document_adapter if document_adapter else DynamoAdapter(self._session)
        )

        self._client = self._session.client("ssm")

        self._environment = environment or os.getenv("PICPAY_OWL_ENVIRONMENT", "prod")

        self._data = None

    def get_table(self):

        if self._data:
            return self._data

        environment = self._environment
        collection = self.get_parameter("configuration_collections")

        match = {"environment": environment}

        self._data = self._document_adapter.read(collection, match)

        return self._data

    def get_parameter(self, parameter_name: str) -> Any:
        """Retrieve a parameter from the parameter store
        Args:
            parameter_name (str): The name of the parameter to be requested
            session (Optional): The session to connect with Amazon aws
        Returns:
            str: The value of the required parameter
        """
        parameter_path = f"/owl/lib/{self._environment}/{parameter_name.lower()}"

        if parameter_name in os.environ:
            return os.environ[parameter_name]

        try:
            print(parameter_path)
            parameter = self._client.get_parameter(
                Name=parameter_path, WithDecryption=True
            )
        except self._client.exceptions.ParameterNotFound:  # type: ignore # pragma: no cover
            msg = f"The parameter {parameter_name} has not found on parameter Store"
            logger.info(msg)
            return None

        except self._client.exceptions.ParameterVersionNotFound:  # type: ignore # pragma: no cover
            msg = f"The parameter version for {parameter_name} has not found on parameter Store"
            logger.info(msg)
            return None

        except self._client.exceptions.InvalidKeyId:  # type: ignore # pragma: no cover
            msg = (
                f"Invalid key Id for {parameter_name} has not found on parameter Store"
            )
            logger.info(msg)
            return None

        except self._client.exceptions.InternalServerError:  # type: ignore # pragma: no cover
            msg = f"Internal sever error while acessing the paramter store"
            logger.info(msg)
            return None

        if not parameter["Parameter"]["Type"] == "SecureString":
            os.environ[parameter_name] = parameter["Parameter"]["Value"]

        return parameter["Parameter"]["Value"]