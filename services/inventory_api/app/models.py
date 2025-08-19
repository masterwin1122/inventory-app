from sqlalchemy import Column, Integer, String
from .database import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    location = Column(String(120), nullable=True)
