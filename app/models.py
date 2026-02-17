from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from enum import Enum

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CLOSED = "CLOSED"
    FAILED = "FAILED"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    api_key: str = Field(unique=True, index=True)
    accounts: "BrokerAccount" = Relationship(back_populates="user")
    orders: list["Order"] = Relationship(back_populates="user")

class BrokerAccount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    broker_name: str
    broker_api_key: str
    user: Optional[User] = Relationship(back_populates="accounts")

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    symbol: str
    side: OrderSide
    quantity: float = 1.0 # Default lot size
    price: Optional[float] = None # Entry price
    sl: Optional[float] = None
    tp: Optional[float] = None
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    broker_order_id: Optional[str] = None
    pnl: Optional[float] = None # For analytics
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

    user: Optional[User] = Relationship(back_populates="orders")
