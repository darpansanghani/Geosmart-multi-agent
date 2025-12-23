# GeoSmart Multi-Agent Grievance System

A **true multi-agent AI system** for intelligent civic complaint management, built for Agentathon 2025.

## 🎯 What Makes This "Agentic"?

This is **not** just multiple AI API calls. It's a genuine multi-agent system with:

- **6 Specialized Autonomous Agents** working collaboratively
- **Shared Context/Memory** - agents build upon each other's findings
- **Dynamic Workflow** - coordinator intelligently decides which agents to run
- **Full Explainability** - track every agent's contribution and decision
- **Extensible Architecture** - add new agents without modifying existing ones

## 🤖 Multi-Agent Architecture

### The Agents

1. **Coordinator Agent** - Orchestrates workflow and manages shared context
2. **Understanding Agent** - Extracts entities & intent from complaint text
3. **GIS Intelligence Agent** - Enriches with geospatial data (zones, wards, nearby facilities)
4. **Classification Agent** - Determines category, severity, and impact scope
5. **Routing Agent** - Autonomously assigns to appropriate departments
6. **Action Planning Agent** - Creates specific, actionable resolution plans

### How They Collaborate

```
User Complaint
    ↓
Coordinator Agent (orchestrates)
    ↓
Understanding Agent → writes to Shared Context
    ↓                       ↓
GIS Agent → reads context → adds geo data
    ↓                       ↓
Classification Agent → reads both → determines severity
    ↓                       ↓
Routing Agent → reads severity + location → assigns department
    ↓                       ↓
Action Planning Agent → reads all → creates action plan
    ↓
Final Result with Full Traceability
```

## 📁 Project Structure

```
geosmart-multi-agent/
├── backend/                    # Express.js backend
│   ├── agents/                 # Multi-agent system
│   │   ├── coordinator.js
│   │   ├── context.js
│   │   ├── understandingAgent.js
│   │   ├── gisAgent.js
│   │   ├── classificationAgent.js
│   │   ├── routingAgent.js
│   │   └── actionPlanningAgent.js
│   ├── routes/
│   ├── db/
│   ├── data/                   # GeoJSON zone data
│   └── server.js
│
├── frontend/                   # React + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map.jsx
│   │   │   ├── ComplaintForm.jsx
│   │   │   ├── AgentExecutionTimeline.jsx
│   │   │   └── AIResultCard.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── index.css
│
└── docs/                       # Documentation
    ├── API.md
    ├── ARCHITECTURE.md
    └── SETUP.md
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 14+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd geosmart-multi-agent
   ```

2. **Set up backend**
   ```bash
   cd backend
   npm install
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY and database credentials
   npm run db:setup  # Create database and run migrations
   ```

3. **Set up frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Run the application**
   ```bash
   # Terminal 1 - Backend
   cd backend
   npm run dev

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

5. **Open browser**
   Navigate to `http://localhost:5173`

## 🎬 Demo Flow

### 1. Submit a Complaint
Enter: *"Garbage pile near Apollo Hospital for 3 days"* with location

### 2. Watch Multi-Agent Execution
Real-time timeline shows:
```
✓ Understanding Agent (780ms)
  → Detected: Garbage accumulation, High urgency, 3-day duration

✓ GIS Intelligence Agent (450ms)
  → Zone: Khairatabad, Ward: 115
  → Proximity: Apollo Hospital

✓ Classification Agent (920ms)
  → Severity: HIGH (medical facility proximity)

✓ Routing Agent (680ms)
  → Department: GHMC Sanitation, Ward 115

✓ Action Planning Agent (510ms)
  → 3-step plan, 4-hour timeline
```

### 3. See Adaptive Behavior
Submit simple complaint: *"Small pothole on quiet street"*
- System skips Routing & Action Planning (low severity)
- Demonstrates **intelligent orchestration**!

## 🏗️ Tech Stack

**Frontend:**
- React 18 + Vite
- Leaflet.js (maps)
- Vanilla CSS (modern glassmorphism design)

**Backend:**
- Express.js
- PostgreSQL
- Google Gemini API

**GIS:**
- Turf.js (geospatial calculations)
- GeoJSON (zone/ward boundaries)

## 📊 Database Schema

### Tables
- `complaints` - Complaint records
- `agent_executions` - Track each agent's execution
- `agent_context` - Shared context storage
- `zones` - GIS zone/ward data (optional)

See [docs/DATABASE.md](docs/DATABASE.md) for full schema.

## 🔌 API Endpoints

### POST `/api/complaints`
Submit new complaint (triggers multi-agent processing)

### GET `/api/complaints`
List all complaints with filters

### GET `/api/complaints/:id`
Get complaint details with agent execution trace

See [docs/API.md](docs/API.md) for complete API documentation.

## 🏆 Why This Wins

### True Agentic AI
- ✅ Autonomy - each agent makes independent decisions
- ✅ Collaboration - agents share context and build on each other
- ✅ Specialization - domain-specific expertise
- ✅ Orchestration - intelligent workflow management
- ✅ Explainability - full traceability of decisions

### vs. Single-Agent Approaches
Most solutions: One AI call → One result

**Our approach:**
- Multiple specialized agents
- Shared context
- Dynamic orchestration
- Emergent intelligence

## 🛠️ Development

### Adding a New Agent

1. Create new agent file: `backend/agents/yourAgent.js`
2. Implement `execute(context)` method
3. Update coordinator to include your agent
4. Done! No other changes needed.

Example:
```javascript
class SentimentAgent {
  async execute(context) {
    const text = context.get('original_text');
    // Your logic here
    context.update('SentimentAgent', {
      sentiment: 'positive',
      emotion: 'frustrated'
    });
    return { summary: 'Sentiment analyzed' };
  }
}
```

## 📝 License

MIT

## 👥 Team

Built by Team GeoSmart for Agentathon 2025

---

**This is agentic AI done right.** 🚀
