from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Relationship

class ProductBase(SQLModel):
    product_name : str
    product_url: str

# 2. Model for API input (POST requests) - No ID required or accepted
class ProductCreate(ProductBase):
    pass

# 3. Database table model - Adds auto-incrementing primary key ID
class Product(ProductBase, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    pricehistory: List[PriceHistory] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class PriceHistory(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    price: float
    # Use timezone-aware UTC datetime for SQLModel compatibility
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    product: Optional[Product] = Relationship(back_populates="pricehistory")

engine = create_engine("sqlite:///database.db")

def init_db():
    SQLModel.metadata.create_all(engine)