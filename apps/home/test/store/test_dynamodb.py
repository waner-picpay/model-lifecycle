import os
import pytest
import re
import json
import sys 
sys.path.append('../../')

from boto3.session import Session
from boto3.dynamodb.conditions import Key
from decimal import Decimal
from botocore.exceptions import ClientError
from factories.session import Boto3SessionFactory
from factories.configuration import ConfigurationFactory

from store.dynamodb import DynamoAdapter
from copy import deepcopy
from factories.logger import LoggerFactory

logger = LoggerFactory.get_logger(__name__)

EXP_QUERY = {
    "IndexName": "experiment_name-index",
    "KeyConditionExpression": "#exp_name = :exp_name",
    "ExpressionAttributeNames": {"#exp_name": "experiment_name"},
    "ExpressionAttributeValues": {":exp_name": {"S": ""}},
}


@pytest.fixture
def prepare_session():

    session = Boto3SessionFactory.get_or_create()
    return session


@pytest.fixture
def create_content():
    return {
        "run_name": "test_id2",
        "experiment_name": "exp_1",
        "value": "test_value",
        "test_list": ["b", "c", "d"],
        "test_data": "2021-21-21T123123",
        "numeric": 1234,
        "decimal": 120.3221323423,
    }


@pytest.fixture
def prepare_collection(prepare_session):

    session = prepare_session

    configuration = ConfigurationFactory.get_or_create(session, "tests")
    collection = configuration.get_parameter("run_collections")

    return collection


@pytest.fixture
def prepare_write(prepare_session, create_content, prepare_collection):

    session = prepare_session
    collection = prepare_collection
    content = create_content
    key = "run_name"

    database = session.resource("dynamodb")
    table = database.Table(collection)

    yield session, content, collection, key

    table.delete_item(Key={key: content[key]})


@pytest.fixture
def prepare_update(prepare_session, create_content, prepare_collection):

    session = prepare_session
    content = create_content
    collection = prepare_collection
    key = "run_name"

    database = session.resource("dynamodb")
    table = database.Table(collection)

    content = json.loads(json.dumps(content), parse_float=Decimal)

    table.put_item(Item=content)

    yield session, content, collection, key, table

    table.delete_item(Key={key: content[key]})


def test_read_with_success(prepare_update):

    session = prepare_update[0]
    content = prepare_update[1]
    collection = prepare_update[2]
    key = prepare_update[3]

    dynamo_db = DynamoAdapter(session)

    result = dynamo_db.read(collection, {key: content[key]})

    assert result == content


def test_read_with_error(prepare_update):

    session = prepare_update[0]
    content = prepare_update[1]
    collection = prepare_update[2]
    key = prepare_update[3]

    dynamo_db = DynamoAdapter(session)

    resunt = dynamo_db.read(collection, {key: "ERROR"})

    assert resunt == None

    with pytest.raises(
        ClientError, match="The provided key element does not match the schema"
    ):
        dynamo_db.read(collection, {"ERROR": "ERROR"})

    with pytest.raises(
        Exception,
        match=re.escape(
            "An error occurred (ResourceNotFoundException) when calling the GetItem operation: Requested resource not found"
        ),
    ):
        dynamo_db.read("ERROR", {key: content[key]})


def test_query_with_success(prepare_update):

    session = prepare_update[0]
    content = prepare_update[1]
    collection = prepare_update[2]
    value = "exp_1"

    dynamo_db = DynamoAdapter(session)

    query_dict = deepcopy(EXP_QUERY)
    query_dict["ExpressionAttributeValues"][":exp_name"] = value

    result = dynamo_db.query_custom(collection=collection, query_dict=query_dict)

    result = result[0]

    assert len(result) == 1

    assert result == [content]

    assert result[0] == content


def test_scan(prepare_session, prepare_collection):
    session = prepare_session
    collection = prepare_collection

    dynamo_db = DynamoAdapter(session)

    result, offset = dynamo_db.scan(collection, limit=2, offset=None)

    assert len(result) == 2

    result, offset = dynamo_db.scan(collection, offset=offset, limit=1)

    assert len(result) == 1