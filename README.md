# GeoSmart Multi-Agent Grievance System
A specialized multi-agent system for processing, classifying, and resolving civic grievances with geospatial intelligence.

**Powered by Python (FastAPI) & React.**
> **Note**: This project utilizes `backend_py` as the active backend directory

## 🏗 Architecture
The system consists of:
1.  **Frontend**: React (Vite) application.
2.  **Backend**: Python (FastAPI) application governing 7 AI agents.
### Agents (Python)
*   **Coordinator Agent**: Orchestrator.
*   **Understanding Agent**: Parses intent & urgency.
*   **GIS Agent**: Geospatial analysis (Zones: Secunderabad, Charminar, etc.).
*   **Classification Agent**: Severity & Category determination.
*   **Routing Agent**: Assigns departments (e.g., Disaster Management).
*   **Sentiment/Predictive/Action Agents**: Auxiliary intelligence.
---

## 📂 Project Structure
```
geosmart-multi-agent/
├── backend_py/             # <--- ACTIVE PYTHON BACKEND
│   ├── agents/             # AI Agent logic (Gemini powered)
│   ├── routers/            # FastAPI endpoints
│   ├── db/                 # Database connection & setup
│   ├── app.py              # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
├── frontend/               # React Frontend
│   ├── src/
│   └── vite.config.js
└── README.md               # This file
```
---

## ⚡ Quick Start Guide
### 1. Prerequisites
*   Node.js (Frontend)
*   Python 3.10+ (Backend)
*   PostgreSQL (Database)
*   Google Gemini API Key

### 2. Backend Setup (In `backend_py/`)
1.  **Navigate directly to the Python backend:**
    ```bash
    cd backend_py
    ```
2.  **Configure Environment:**
    Copy the example env file and add your keys:
    ```bash
    cp .env.example .env
    # Edit .env with your credentials
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Database Setup:**
    ```bash
    python db/setup.py
    ```
5.  **Run the Server:**
    ```bash
    python -m uvicorn backend_py.app:app --host 0.0.0.0 --port 3000 --reload
    ```
    *Server will start at `http://localhost:3000`*

### 3. Frontend Setup (In `frontend/`)
1.  **Navigate to frontend:**
    ```bash
    cd ../frontend
    ```
2.  **Install & Run:**
    ```bash
    npm install
    npm run dev
    ```
    *App will start at `http://localhost:5173`*
---

## 🧪 Verification & Testing
To test the AI Agents without the frontend:
```bash
cd backend_py
# Test 1: Verify Agent Logic (Zone detection, Severity classification)
python ../debug_agents.py
# (Note: debug_agents.py is in the root, run it from root or adjust path)
```
*Tip: To run the debug script from the root:*
```bash
# From project root
python debug_agents.py
```

## ⚠️ Troubleshooting
*   **Wrong Zone?**
    Ensure you are using `backend_py`. The GIS Agent covers most of Hyderabad. If outside, it may default or fail safely.
*   **Severity "Low"?**
    Critical words like "accident", "fire", "dead" trigger HIGH severity. Routine issues (roads, sanitation) default to MEDIUM.
*   **"Form data requires python-multipart"**:
    Run `pip install python-multipart` if you see this error (already included in requirements).