from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select
from app.database import engine
from app.models import Order, User, BrokerAccount
from app.services.parser import SignalParser
from app.services.broker import MockBroker
from app.api.websockets import manager

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

@router.post("/webhook/receive-signal")
async def receive_signal(signal_text: str, user_id: int = 1, background_tasks: BackgroundTasks = BackgroundTasks(), session: Session = Depends(get_session)):
    """
    Receives a trading signal, parses it, and triggers background execution.
    Optional: user_id query param to simulate different users.
    """
    try:
        # 1. Parse Data
        data = SignalParser.parse(signal_text)
        
        # 2. Create Order Record (Status: PENDING)
        # Check if user exists, create if missing
        user = session.get(User, user_id)
        if not user:
            user = User(id=user_id, username=f"trader_{user_id}", api_key=f"key-{user_id}")
            session.add(user)
            session.commit()
            session.refresh(user)

        new_order = Order(
            user_id=user.id,
            symbol=data["symbol"],
            side=data["side"],
            price=data["price"],
            sl=data["sl"],
            tp=data["tp"],
            status="PENDING"
        )
        session.add(new_order)
        session.commit()
        session.refresh(new_order)

        # 3. Queue Background Execution
        background_tasks.add_task(MockBroker.execute_order, new_order.id)
        
        return {"status": "received", "order_id": new_order.id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders")
def get_orders(session: Session = Depends(get_session)):
    orders = session.exec(select(Order)).all()
    return orders

@router.get("/orders/{order_id}")
def get_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/accounts")
def link_broker_account(account: BrokerAccount, session: Session = Depends(get_session)):
    """
    Links a broker account to a user.
    """
    # Check if user exists, if not create (for demo simplicity)
    user = session.get(User, account.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.websocket("/ws/orders")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
             # Keep connection implementation alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/analytics")
def get_analytics(session: Session = Depends(get_session)):
    """
    Bonus: Simple analytics for closed orders.
    """
    closed_orders = session.exec(select(Order).where(Order.status == "CLOSED")).all()
    if not closed_orders:
        return {"total_trades": 0, "win_rate": 0, "total_pnl": 0}

    total_pnl = sum(o.pnl for o in closed_orders)
    wins = len([o for o in closed_orders if o.pnl > 0])
    win_rate = (wins / len(closed_orders)) * 100

    return {
        "total_trades": len(closed_orders),
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2)
    }
