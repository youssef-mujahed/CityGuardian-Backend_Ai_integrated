from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class Location(BaseModel):
    latitude: float
    longitude: float

class PaginationResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int