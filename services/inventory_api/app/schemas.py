from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64)
    name: str
    quantity: int = 0
    location: str | None = None

class ItemUpdate(BaseModel):
    name: str | None = None
    quantity: int | None = None
    location: str | None = None

class ItemRead(BaseModel):
    id: int
    sku: str
    name: str
    quantity: int
    location: str | None = None

    class Config:
        from_attributes = True
