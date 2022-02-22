import os

from factories.session import Boto3SessionFactory
from store.dynamodb import DynamoAdapter

s3_session = Boto3SessionFactory.get_or_create()
db_adapter = DynamoAdapter(s3_session)
