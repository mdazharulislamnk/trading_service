import asyncio
import uuid
import random
from datetime import datetime
from sqlmodel import Session, select
from app.models import Order, OrderStatus
from app.database import engine

# Simple WebSocket manager placeholder (will be implemented fully in endpoints)
from app.api.websockets import manager

class MockBroker:
    @staticmethod
    async def execute_order(order_id: int):
        """
        Simulates the lifecycle of an order: Pending -> Executed -> Closed
        """
        await asyncio.sleep(2) # Simulate network delay
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                return

            # 1. Update to EXECUTED
            order.status = OrderStatus.EXECUTED
            order.broker_order_id = str(uuid.uuid4())
            session.add(order)
            session.commit()
            session.refresh(order)
            
            print(f"✅ Order {order.id} EXECUTED. Broker ID: {order.broker_order_id}")
            await manager.broadcast(f"Order {order.id} EXECUTED at {order.price}")

            # 2. Simulate holding period then CLOSE (for analytics demo)
            await asyncio.sleep(5) 
            
            # Randomly decide win or loss for analytics
            is_win = random.choice([True, False])
            pnl = random.uniform(10, 50) if is_win else random.uniform(-10, -50)
            
            order.status = OrderStatus.CLOSED
            order.pnl = round(pnl, 2)
            order.closed_at = datetime.utcnow()
            
            session.add(order)
            session.commit()
            
            print(f"🏁 Order {order.id} CLOSED. PnL: {order.pnl}")
            await manager.broadcast(f"Order {order.id} CLOSED. PnL: {order.pnl}")

