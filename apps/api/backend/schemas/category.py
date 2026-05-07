from pydantic import BaseModel
from uuid import UUID

class CategoryResponse(BaseModel):
    category_id: UUID
    category_name: str
    category_depth: int
    category_status: str