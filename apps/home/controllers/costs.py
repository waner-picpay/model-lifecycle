import boto3

client = boto3.client('ce')

response = client.get_cost_and_usage(
    TimePeriod={
        'Start': '2022-01-01',
        'End': '2022-01-31'
    },
    Granularity='MONTHLY',
    # Filter={
    #     'Or': [
    #         {'... recursive ...'},
    #     ],
    #     'And': [
    #         {'... recursive ...'},
    #     ],
    #     'Not': {'... recursive ...'},
    #     'Dimensions': {
    #         'Key': 'AZ'|'INSTANCE_TYPE'|'LINKED_ACCOUNT'|'OPERATION'|'PURCHASE_TYPE'|'REGION'|'SERVICE'|'USAGE_TYPE'|'USAGE_TYPE_GROUP'|'RECORD_TYPE'|'OPERATING_SYSTEM'|'TENANCY'|'SCOPE'|'PLATFORM'|'SUBSCRIPTION_ID'|'LEGAL_ENTITY_NAME'|'DEPLOYMENT_OPTION'|'DATABASE_ENGINE'|'CACHE_ENGINE'|'INSTANCE_TYPE_FAMILY'|'BILLING_ENTITY'|'RESERVATION_ID',
    #         'Values': [
    #             'string',
    #         ]
    #     },
    #     'Tags': {
    #         'Key': 'string',
    #         'Values': [
    #             'string',
    #         ]
    #     }
    # },
    Metrics=[
        'BLENDED_COST',
    ],
    GroupBy=[
        {
            'Type': 'TAG',
            'Key': 'ProcessType'
        },
    ],
    # NextPageToken='string'
)
print(response)
