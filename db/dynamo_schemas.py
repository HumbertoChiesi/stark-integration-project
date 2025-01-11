from pydantic import BaseModel
from typing import ClassVar


class BasicTable(BaseModel):
    table_name: ClassVar[str]
    hash_key: ClassVar[str]
    sort_key: str | None = None

    def get_keys(self) -> dict:
        keys = {self.hash_key: getattr(self, self.hash_key)}
        if self.sort_key:
            keys[self.sort_key] = getattr(self, self.sort_key)
        return self.convert_to_dynamo(keys)

    def to_dynamo(self) -> dict:
        return self.convert_to_dynamo(self.model_dump(exclude_none=True))

    @classmethod
    def from_dynamo(cls, data: dict):
        return cls(**data)
    
    @staticmethod
    def convert_to_dynamo(obj: dict) -> dict:
        dynamo_item = {}

        for key, value in obj.items():
            if isinstance(value, str):
                dynamo_item[key] = {'S': value}
            elif isinstance(value, bool):
                dynamo_item[key] = {'BOOL': value}
            elif isinstance(value, (int, float)):
                dynamo_item[key] = {'N': str(value)}

        return dynamo_item


class LambdaMetrics(BasicTable):
    lambdaName: str
    callCount: int | None = None

    table_name: ClassVar[str] = "LambdaMetrics"
    hash_key: ClassVar[str] = 'lambdaName'
    sort_key: ClassVar[str|None] = None

class LambdaErrorsLog(BasicTable):
    lambdaName: str
    executionId: str
    payload: str | None = None
    errorMessage: str | None = None
    
    table_name: ClassVar[str] = "LambdaErrorsLog"
    hash_key: ClassVar[str] = 'lambdaName'
    sort_key: ClassVar[str | None] = "executionId"