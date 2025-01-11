from typing import TypeVar
from .dynamo_schemas import BasicTable
import boto3

T = TypeVar('T', bound=BasicTable)

class DDB:
    client = boto3.client("dynamodb")

    def save(self, obj: BasicTable):
        """# Save Item to DynamoDB
        Saves an item (object) to its DynamoDB table.
        ## Parameters (required):
        - obj [BasicTable]: instance of a class that inherits from `BasicTable`.
        ## Return:
        - None
        """
        table_name = obj.table_name
        dynamo_item = obj.to_dynamo()

        self.client.put_item(
            TableName=table_name,
            Item=dynamo_item
        )

    def load(self, db_cls: T, hash_key: str, sort_key: str | None = None) -> T | None:
        """# Load Item from DynamoDB
        Retrieves an item from DynamoDB based on the provided hash key and optional sort key.
        ## Parameters (required):
        - db_cls [Type[T]]: A class that inherits from `BasicTable`.
        - hash_key [str]: The hash key value used to identify the item in DynamoDB.
        ## Parameters (optional):
        - sort_key [str, default None]: The sort key value used to further identify the item. If not provided, only the hash key is used.
        ## Return:
        - T or None: The instance of `db_cls` populated with the retrieved data, or None if no item is found.
        """
        table_name = db_cls.table_name

        keys = {db_cls.hash_key: {'S': hash_key}}
        if db_cls.sort_key and sort_key:
            keys[db_cls.sort_key] = {'S': sort_key}
        
        response = self.client.get_item(
            TableName=table_name,
            Key=keys
        )

        item = response.get('Item')
        if not item:
            return None

        record = {k: list(v.values())[0] for k, v in item.items()}
        return db_cls.from_dynamo(record)
        
    def delete(self, obj: BasicTable):
        """# Delete Item from DynamoDB
        Deletes an item from the specified DynamoDB table.
        ## Parameters (required):
        - obj [BasicTable]: instance of a class that inherits from `BasicTable`.
        ## Return:
        None
        """
        table_name = obj.table_name
        key = obj.get_keys()

        self.client.delete_item(
            TableName=table_name,
            Key=key
        )
