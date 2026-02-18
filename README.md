# Trading Signal Service 

Hi, I'm **Md. Azharul Islam**. This is a backend service I built to handle trading signals, manage order lifecycles, and push updates in real-time. I used **FastAPI**, **PostgreSQL**, and **Docker** to put it all together.

## 📋 Table of Contents

1.  [Project Overview](#project-overview)
2.  [Key Features](#key-features)
3.  [Technology Stack](#technology-stack)
4.  [Project Structure & File Descriptions](#project-structure)
5.  [Getting Started](#getting-started)
    *   [Prerequisites](#prerequisites)
    *   [Running with Docker (Recommended)](#running-with-docker-recommended)
    *   [Running Locally](#running-locally)
6.  [API Documentation](#api-documentation)
7.  [Testing](#testing)
    *   [Visual Dashboard](#visual-dashboard)
    *   [CLI Testing](#cli-testing)
8.  [Design Decisions](#design-decisions)

---

## <a name="project-overview"></a>Project Overview

I wanted to build a system that could "listen" for trading signals (like webhooks from TradingView) and actually do something with them.

The idea was to take a simple text signal, parse it to figure out if it's a BUY or SELL, and then simulate placing that trade.

I made sure it was **asynchronous** and **real-time** because nobody likes waiting:
*   **Signals** get processed in the background, keeping the API responsive.
*   **Status Updates** happen instantly via WebSockets (e.g., whenever an order fills).
*   **Data** is stored securely in a PostgreSQL database.

---

## <a name="key-features"></a>Key Features

*   **Smart Parsing:** I wrote some custom Regex logic to handle different signal formats (like `BUY EURUSD` with or without extra details).
*   **Order Tracking:** The system follows an order from start to finish: `PENDING` -> `EXECUTED` -> `CLOSED`.
*   **Routing:** You can specify `user_id` to route signals to specific accounts.
*   **Mock Broker:** Since I didn't want to connect a real broker account for testing, I built a simulation service that holds orders briefly and then generates a random PnL.
*   **Real-time Feed:** No need to refresh. Updates show up as they happen.
*   **Analytics:** A simple endpoint I added to track Win Rate.
*   **Dockerized:** I wrapped everything in Docker so it's easy to run.

---

## <a name="technology-stack"></a>Technology Stack

*   **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.9+) - I chose this because it's fast and handles async code much better than older frameworks.
*   **Database:** [PostgreSQL](https://www.postgresql.org/) - A solid, production-grade database.
*   **ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) - Makes interacting with the DB feel like writing normal Python classes.
*   **Real-time:** Native WebSockets.
*   **Containerization:** Docker & Docker Compose.

---

## <a name="project-structure"></a>Project Structure & File Descriptions

Here's a breakdown of the codebase and what each file does:

```text
trading_service/
├── app/
│   ├── api/
│   │   ├── endpoints.py    # The API Routes. Handles webhooks, orders, and analytics.
│   │   └── websockets.py   # Connection Manager. Manages who's online and sends updates.
│   ├── services/
│   │   ├── broker.py       # "Mock Broker". Simulates execution delays and market results.
│   │   └── parser.py       # Parsing Logic. Extracts Symbol, Price, SL, and TP.
│   ├── database.py         # Database Setup. Connects to PostgreSQL.
│   ├── main.py             # Entry Point. Starts the app, handles CORS, and the root endpoint.
│   └── models.py           # Database Schema. Defines "User" and "Order" structure.
├── Dockerfile              # Instructions for building the Python environment in Docker.
├── docker-compose.yml      # Startup Script. Launches the API and Database.
├── requirements.txt        # Library List. Installs FastAPI, SQLModel, etc.
├── dashboard.html          # Testing UI. A visual dashboard for testing the API.
├── test_client.html        # Simple Client. Basic file to test WebSocket connections.
├── curl.txt                # CLI Cheat Sheet. Commands for terminal testing.
├── render.yaml             # Render Deployment. Automates setting up the Web Service and DB on Render.
├── .gitignore              # Git Ignore. Prevents files like venv or .db from being committed.
└── README.md               # Documentation. This file.
```

---

## <a name="getting-started"></a>Getting Started

### Prerequisites

*   **Docker Desktop** (Recommended - simplest way)
*   *Or* Python 3.9+ and PostgreSQL installed.

### Running with Docker (Recommended)

1.  **Clone the repo:**
    ```bash
    git clone <repository_url>
    cd trading_service
    ```

2.  **Start the app:**
    ```bash
    docker-compose up --build
    ```

3.  **Check if it works:**
    *   API is available at: `http://localhost:8080`
    *   Docs are available at: `http://localhost:8080/docs`

### Deployment (Render)

I've included a `render.yaml` file so you can deploy this easily:

1.  Push this repo to your GitHub.
2.  Go to [Render Dashboard](https://dashboard.render.com/).
3.  Click **New +** -> **Blueprint**.
4.  Connect your repo.
5.  Render will automatically create the **Web Service** and **PostgreSQL Database** for you.

### Running Locally

1.  **Create a virtual env:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

2.  **Install libraries:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the server:**
    ```bash
    uvicorn app.main:app --reload --port 8080
    ```

---

## <a name="api-documentation"></a>API Documentation

Full interactive documentation is available at **`http://localhost:8080/docs`**.

### Core Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root endpoint. Lists paths and usage examples. |
| `GET` | `/health` | Simple check to see if the service is running. |
| `POST` | `/webhook/receive-signal` | Endpoint to receive user signals. |
| `GET` | `/orders` | Lists all orders for a user. |
| `GET` | `/orders/{id}` | Gets details for a specific order. |
| `POST` | `/accounts` | Links a broker account to a user. |
| `GET` | `/analytics` | Shows simple analytics for closed orders. |
| `GET` | `/dashboard` | UI for testing the API and viewing orders. |
| `WS` | `/ws/orders` | WebSocket for real-time order updates. |

---

## <a name="testing"></a>Testing

### 1. Visual Dashboard (GUI)
I've included a dashboard at **`http://localhost:8080/dashboard`**. Open it to:
*   Check WebSocket connection.
*   Send test signals for different users (via POST).
*   Watch orders update in real-time.

### 2. CLI Testing
You can test endpoints using `curl`. **Note:** On Windows, use double quotes `"` around URLs.

```bash
# Health Check
curl -X GET "http://localhost:8080/health"

# Send a BUY signal for User 1
curl -X POST "http://localhost:8080/webhook/receive-signal?user_id=1&signal_text=BUY%20EURUSD%20%401.0850%0ASL%201.0800%0ATP%201.0900"
```

---

## <a name="design-decisions"></a>Design Decisions

### Why FastAPI?
I needed something performant that could handle concurrency well. I've used Django, but FastAPI is quicker for this kind of work and has great native support for async tasks (like WebSockets).

### Regular Expressions (Regex)
Parsing trading signals can be tricky since formats vary. Regex gave me enough flexibility to handle signals whether or not they included an entry price, making the system more robust without overcomplicating it.

### Database Choice
I chose **PostgreSQL** (via Docker) over SQLite because I wanted to set up a proper, production-ready environment, even for a test project.

---

**Author:** Md. Azharul Islam
