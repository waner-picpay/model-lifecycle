

class FeaturesController:
    QUERY = {
        "IndexName": "name-origin-index",
        "KeyConditionExpression": "#name = :name",
        "ExpressionAttributeNames": {"#name": "name"},
        "ExpressionAttributeValues": {":name": {"S": ""}},
    }

    def __init__(self) -> None:
        pass
