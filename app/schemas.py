from pydantic import BaseModel, ConfigDict


# --- Orders ---
class OrderCreateSchema(BaseModel):
    order_id: int
    item: str
    price: float


class OrderResponseSchema(OrderCreateSchema):
    status: str
    model_config = ConfigDict(from_attributes=True)


class StatusUpdateSchema(BaseModel):
    status: str


# --- Items ---
class ItemSchema(BaseModel):
    id: int
    name: str
    price: float
    model_config = ConfigDict(from_attributes=True)