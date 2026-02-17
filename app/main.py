from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.api import endpoints

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Trading Signal Service",
    description="A backend service to process trading signals and execute mock trades.",
    version="1.0.0"
)

# Allow CORS for local testing (file:// and localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)

from app.database import create_db_and_tables

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is running"}

@app.get("/")
def root():
    return {
        "message": "Trading Service API",
        "endpoints": [
            {
                "Purpose": "Health Check",
                "Endpoint": "/health",
                "Method": "GET",
                "Description": "A simple endpoint to check if your service is running."
            },
            {
                "Purpose": "Signal Webhook",
                "Endpoint": "/webhook/receive-signal",
                "Method": "POST",
                "Description": "The URL that receives signals from user."
            },
            {
                "Purpose": "Get Orders",
                "Endpoint": "/orders",
                "Method": "GET",
                "Description": "Get a list of all orders for a user."
            },
            {
                "Purpose": "Get Order Details",
                "Endpoint": "/orders/{id}",
                "Method": "GET",
                "Description": "Get the details of a single order."
            },
            {
                "Purpose": "Link Broker Account",
                "Endpoint": "/accounts",
                "Method": "POST",
                "Description": "A way for a user to add their broker account details."
            },
            {
                "Purpose": "Get Analytics",
                "Endpoint": "/analytics",
                "Method": "GET",
                "Description": "Simple analytics for closed orders."
            },
            {
                "Purpose": "User Dashboard",
                "Endpoint": "/dashboard",
                "Method": "GET",
                "Description": "A UI to test the API and view orders."
            },
            {
                "Purpose": "Real-time Orders",
                "Endpoint": "/ws/orders",
                "Method": "WS",
                "Description": "WebSocket connection for real-time order updates."
            },
            {
                "Purpose": "API Documentation",
                "Endpoint": "/docs",
                "Method": "GET",
                "Description": "Interactive API documentation (Swagger UI)."
            }
        ],
        "usage_examples": {
            "1. Health Check": "curl -X GET \"http://localhost:8080/health\"",
            "2. Send Signal (User 1 - Buy EURUSD)": "curl -X POST \"http://localhost:8080/webhook/receive-signal?user_id=1&signal_text=BUY%20EURUSD%20%401.0850%0ASL%201.0800%0ATP%201.0900\"",
            "3. Send Signal (User 2 - Sell GBPUSD)": "curl -X POST \"http://localhost:8080/webhook/receive-signal?user_id=2&signal_text=SELL%20GBPUSD%20%401.2500%0ASL%201.2600%0ATP%201.2400\"",
            "4. Send Signal (User 99 - Buy BTCUSD)": "curl -X POST \"http://localhost:8080/webhook/receive-signal?user_id=99&signal_text=BUY%20BTCUSD%20%4065000\"",
            "5. Get All Orders": "curl -X GET \"http://localhost:8080/orders\"",
            "6. Get Specific Order (ID 1)": "curl -X GET \"http://localhost:8080/orders/1\"",
            "7. Link Broker Account (Generic)": "curl -X POST \"http://localhost:8080/accounts\" -H \"Content-Type: application/json\" -d \"{\\\"user_id\\\": 2, \\\"broker_name\\\": \\\"Binance\\\", \\\"broker_api_key\\\": \\\"key-999\\\"}\"",
            "8. Get Analytics": "curl -X GET \"http://localhost:8080/analytics\""
        }
    }

@app.get("/dashboard")
def dashboard():
    return FileResponse("dashboard.html")
