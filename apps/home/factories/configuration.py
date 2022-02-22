from boto3.session import Session

from store.interfaces import IDocumentAdapter
from utils.configuration import Configuration


class ConfigurationFactory:

    instance = None

    @classmethod
    def get_or_create(
        cls,
        session: Session = None,
        document_adapter: IDocumentAdapter = None,
        environment: str = None,
    ):

        if cls.instance == None:
            cls.instance = Configuration(
                session=session,
                document_adapter=document_adapter,
                environment=environment,
            )

        return cls.instance