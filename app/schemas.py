from pydantic import BaseModel


# --- Orders ---
class OrderCreateSchema(BaseModel):
    order_id: int
    item: str
    price: float


class OrderResponseSchema(OrderCreateSchema):
    status: str

    class Config:
        from_attributes = True


class StatusUpdateSchema(BaseModel):
    status: str


# --- Items ---
class ItemSchema(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True