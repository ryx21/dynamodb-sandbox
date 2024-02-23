import boto3
from typing import Dict, List, Any
from ksuid import Ksuid


# Constants
PK = 'PK'
SK = 'SK'
GSI1PK = 'GSI1PK'
GSI1SK = 'GSI1SK'
ENTITY_TYPE = 'EntityType'
GSI1_NAME = 'GSI_ORDERS'

# Entity types
CUSTOMER_ENTITY = 'CUSTOMER'
ORDER_ENTITY = 'ORDER'
ITEM_ENTITY = 'ITEM'
EMAIL_ADDRESS_ENTITY = 'EMAIL_ADDRESS'

# Customer entity constants
CUSTOMER = 'Customer'
CUSTOMER_USERNAME = 'Username'
CUSTOMER_EMAIL_ADDRESS = 'EmailAddress'
CUSTOMER_ADDRESSES = 'Addresses'
CUSTOMER_NAME = 'Name'

# Order entity constants
ORDER_ID = 'OrderId'
ORDER_CREATED_AT = 'CreatedAt'
ORDER_STATUS = 'Status'
ORDER_AMOUNT = 'Amount'
ORDER_NUMBER_ITEMS = 'NumberItems'

# Item entity constants
ITEM_ID = 'ItemId'
ITEM_PRICE = 'ItemPrice'
ITEM_DESCRIPTION = 'ItemDescription'


# primary and secondary index definitions

ATTRIBUTE_DEFINITIONS = [
    {'AttributeName': PK, 'AttributeType': 'S'},
    {'AttributeName': SK, 'AttributeType': 'S'},
    {'AttributeName': GSI1PK, 'AttributeType': 'S'},
    {'AttributeName': GSI1SK, 'AttributeType': 'S'}
]

PRIMARY_KEY_SCHEMA = [
    {'AttributeName': PK, 'KeyType': 'HASH'},
    {'AttributeName': SK, 'KeyType': 'RANGE'},
]

GSI1_CONFIG = {
    'IndexName': GSI1_NAME,
    'KeySchema': [
        {'AttributeName': GSI1PK, 'KeyType': 'HASH'},
        {'AttributeName': GSI1SK, 'KeyType': 'RANGE'}
    ],
    'Projection': {
        'ProjectionType': 'ALL',
    }
}


class ECommerceTable:

    def __init__(self, table_name: str):
        self.client = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
        self.table_name = table_name

    def create_table(self):
        try:
            self.client.create_table(
                TableName=self.table_name,
                AttributeDefinitions=ATTRIBUTE_DEFINITIONS,
                KeySchema=PRIMARY_KEY_SCHEMA,
                GlobalSecondaryIndexes=[GSI1_CONFIG],
                BillingMode='PAY_PER_REQUEST',
            )
        except self.client.exceptions.ResourceInUseException:
            print(f"Table {self.table_name} already exists, not running setup.")

    def delete_table(self) -> dict:
        response = self.client.delete_table(TableName=self.table_name)
        return response

    def describe_table(self) -> dict:
        return self.client.describe_table(TableName=self.table_name)

    def list_all(self):
        result = self.client.scan(TableName=self.table_name)
        return result

    def create_customer(self, username: str, email_address: str, name: str):
        self.client.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': self.table_name,
                        'Item': {
                            PK: {'S': f'CUSTOMER#{username}'},
                            SK: {'S': f'CUSTOMER#{username}'},
                            ENTITY_TYPE: {'S': CUSTOMER_ENTITY},
                            CUSTOMER_USERNAME: {'S': username},
                            CUSTOMER_EMAIL_ADDRESS: {'S': email_address},
                            CUSTOMER_ADDRESSES: {'M': {}},
                            CUSTOMER_NAME: {'S': name}
                            },
                        'ConditionExpression': 'attribute_not_exists(PK)'
                    },
                },
                {
                    'Put': {
                        'TableName': self.table_name,
                        'Item': {
                            PK: {'S': f'CUSTOMEREMAIL#{email_address}'},
                            SK: {'S': f'CUSTOMEREMAIL#{email_address}'},
                            ENTITY_TYPE: {'S': EMAIL_ADDRESS_ENTITY}
                        },
                        'ConditionExpression': 'attribute_not_exists(PK)'
                    },
                },
            ]
        )

    def add_customer_address(self, username: str, address_name: str, address_details: str):
        """
        You can't update a map attribute that doesn't exist, so we initialise an empty map when the customer is created
        """
        self.client.update_item(
            TableName=self.table_name,
            Key={
                PK: {'S': f'CUSTOMER#{username}'},
                SK: {'S': f'CUSTOMER#{username}'}
            },
            UpdateExpression='SET #address.#name = :address',
            ExpressionAttributeNames={
                '#address': CUSTOMER_ADDRESSES,
                '#name': address_name
            },
            ExpressionAttributeValues={
                ':address': {'S': address_details}
            }
        )

    def delete_customer_address(self, username: str, address_name: str):
        self.client.update_item(
            TableName=self.table_name,
            Key={
                PK: {'S': f'CUSTOMER#{username}'},
                SK: {'S': f'CUSTOMER#{username}'}
            },
            UpdateExpression='REMOVE #address.#name',
            ExpressionAttributeNames={
                '#address': CUSTOMER_ADDRESSES,
                '#name': address_name
            },
        )

    def create_order(self, username: str, order_items: List[Dict[str, Any]]):
        """
        * Should fail if username doesn't exist
        * Generates a sortable order id using ksuid
        * Order items should be a list of dicts containing the following data elements:
         {
            'price': number,
            'description': str
         }
        """
        order_amount = sum(item["price"] for item in order_items)
        number_items = len(order_items)
        order_id = Ksuid()
        self.client.put_item(
            TableName=self.table_name,
            Item={
                PK: {'S': f'CUSTOMER#{username}'},
                SK: {'S': f'#ORDER#{str(order_id)}'},
                GSI1PK: {'S': f'ORDER#{str(order_id)}'},
                GSI1SK: {'S': f'ORDER#{str(order_id)}'},
                ENTITY_TYPE: {'S': ORDER_ENTITY},
                ORDER_ID: {'S': str(order_id)},
                ORDER_CREATED_AT: {'S': str(order_id.datetime.isoformat())},
                ORDER_STATUS: {'S': 'ACCEPTED'},
                ORDER_AMOUNT: {'N': str(order_amount)},
                ORDER_NUMBER_ITEMS: {'N': str(number_items)}
            }
        )
        for item in order_items:
            self._create_order_item(order_id, item)

    def _create_order_item(self, order_id, order_item: Dict[str, Any]):
        item_id = Ksuid()
        self.client.put_item(
            TableName=self.table_name,
            Item={
                PK: {'S': f'#ORDER#ITEM#{str(item_id)}'},
                SK: {'S': f'#ORDER#ITEM#{str(item_id)}'},
                GSI1PK: {'S': f'ORDER#{str(order_id)}'},
                GSI1SK: {'S': f'ITEM#{str(item_id)}'},
                ENTITY_TYPE: {'S': ITEM_ENTITY},
                ORDER_ID: {'S': str(order_id)},
                ITEM_ID: {'S': str(item_id)},
                ITEM_PRICE: {'N': str(order_item["price"])},
                ITEM_DESCRIPTION: {'S': order_item["description"]}
            }
        )

    def update_order_status(self, username:str, order_id: str, status: str):
        self.client.update_item(
            TableName=self.table_name,
            Key={
                PK: {'S': f'CUSTOMER#{username}'},
                SK: {'S': f'#ORDER#{str(order_id)}'}
            },
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={'#status': ORDER_STATUS},
            ExpressionAttributeValues={':status': {'S': status}}
        )

    def get_customer_and_orders(self, username: str, limit: int = 10):
        result = self.client.query(
            TableName=self.table_name,
            KeyConditionExpression='#pk = :pk',
            ExpressionAttributeNames={'#pk': PK},
            ExpressionAttributeValues={':pk': {'S': f'CUSTOMER#{username}'}},
            ScanIndexForward=False,
            Limit=limit + 1
        )
        return result

    def get_order_and_order_items(self, order_id: str, limit: int = 10):
        result = self.client.query(
            TableName=self.table_name,
            IndexName=GSI1_NAME,
            KeyConditionExpression='#gsipk = :gsipk',
            ExpressionAttributeNames={'#gsipk': GSI1PK},
            ExpressionAttributeValues={':gsipk': {'S': f'ORDER#{str(order_id)}'}},
            ScanIndexForward=False,
            Limit=limit + 1
        )
        return result
