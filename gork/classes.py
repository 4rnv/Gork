from typing import NotRequired, TypedDict

class GorkSchema:
    def __init__(self, schema) -> None:
        self.schema = schema

class GorkError(Exception):
    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        super().__init__(message)

class GorkResponse(TypedDict):
    error : NotRequired[str]
    is_valid : bool