import os
from apps.home.factories.configuration import ConfigurationFactory

from apps.home.factories.session import Boto3SessionFactory
from apps.home.store.dynamodb import DynamoAdapter

environment = os.getenv("PICPAY_OWL_ENVIRONMENT", "prod")
session = Boto3SessionFactory.get_or_create()
db_adapter = DynamoAdapter(session)
configuration = ConfigurationFactory.get_or_create(session=session, document_adapter=db_adapter, environment=environment)
