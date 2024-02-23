import boto3
import datetime
from uuid import uuid4


# constants
SESSION_TOKEN = 'SessionToken'
USERNAME = 'UserName'
GSI1_NAME = 'GSI1'
CREATED_AT = 'CreatedAt'
EXPIRES_AT = 'ExpriresAt'
TTL = 'TTL'


class SessionStoreTable:

    def __init__(self, table_name: str):
        self.client = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
        self.table_name = table_name

    def create_table(self):
        """
        Creating a table is an async process - once the below runs, the table has
        an initial TableStatus of "CREATING". Once created, this will be set to
        "ACTIVE". This can be queried with describe table queries. In reality, we
        should be sleeping briefly and waiting for the table to be created before
        doing anything...or maybe calls to the table should check it's active first.
        """
        try:
            self.client.create_table(
                TableName=self.table_name,
                AttributeDefinitions=[
                    {'AttributeName': SESSION_TOKEN, 'AttributeType': 'S'},
                    {'AttributeName': USERNAME, 'AttributeType': 'S'}
                ],
                KeySchema=[
                    {
                        'AttributeName': SESSION_TOKEN,
                        'KeyType': 'HASH'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': GSI1_NAME,
                        'KeySchema': [
                            {
                                'AttributeName': USERNAME,
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': "KEYS_ONLY",
                        }
                    },
                ],
                BillingMode='PAY_PER_REQUEST'
            )

            # enable TTL actually does nothing in DynamoDB local
            # in the cloud, this takes about 1 hour to take effect
            self.client.update_time_to_live(
                TableName=self.table_name,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': TTL
                }
            )
        except self.client.exceptions.ResourceInUseException:
            print(f"Table {self.table_name} already exists, not running setup.")

    def delete_table(self) -> dict:
        response = self.client.delete_table(TableName=self.table_name)
        return response

    def describe_table(self) -> dict:
        """
        This is an eventually consistent query, so in reality we need to handle this.
        """
        return self.client.describe_table(TableName=self.table_name)

    def add_token(self, username: str, time_to_live_seconds: int) -> str:
        token = uuid4()
        create_datetime = datetime.datetime.now()
        expire_datetime = create_datetime + datetime.timedelta(seconds=time_to_live_seconds)
        self.client.put_item(
            TableName=self.table_name,
            Item={
                SESSION_TOKEN: {"S": str(token)},
                USERNAME: {"S": username},
                CREATED_AT: {"S": create_datetime.isoformat()},
                EXPIRES_AT: {"S": expire_datetime.isoformat()},
                TTL: {"N": str(expire_datetime.timestamp())}
            },
            ConditionExpression=f"attribute_not_exists({SESSION_TOKEN})"
        )
        return str(token)

    def list_all(self):
        result = self.client.scan(TableName=self.table_name)
        return result

    def get_token(self, token: str):
        result = self.client.query(
            TableName=self.table_name,
            KeyConditionExpression=f"#token = :token",
            FilterExpression=f"#ttl >= :epoch",
            # Note that 'TTL' is a reserved word, so must use ExpressionAttributeNames
            ExpressionAttributeNames={
                "#token": SESSION_TOKEN,
                "#ttl": TTL
            },
            ExpressionAttributeValues={
                ":token": {"S": token},
                ":epoch": {"N": str(datetime.datetime.now().timestamp())}
            }
        )
        return result

    def delete_token(self, token: str):
        self.client.delete_item(
            TableName=self.table_name,
            Key={SESSION_TOKEN: {"S": token}},
        )
        print(f"Deleted token: {token}")

    def delete_user_tokens(self, user: str):
        user_items = self.client.query(
            TableName=self.table_name,
            IndexName=GSI1_NAME,
            KeyConditionExpression=f"#user = :user",
            ExpressionAttributeNames={
                "#user": USERNAME,
            },
            ExpressionAttributeValues={
                ":user": {"S": user}
            }
        )

        for item in user_items.get("Items", []):
            token = item.get(SESSION_TOKEN, {}).get("S")
            self.delete_token(token)
