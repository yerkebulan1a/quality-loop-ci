from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class OrderModel(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    item = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="pending")


class ItemModel(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)