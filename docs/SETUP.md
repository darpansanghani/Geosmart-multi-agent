# Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 18.x or higher ([Download](https://nodejs.org/))
- **PostgreSQL** 14.x or higher ([Download](https://www.postgresql.org/download/))
- **Git** ([Download](https://git-scm.com/))
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd geosmart-multi-agent
```

### 2. Backend Setup

#### Install Dependencies
```bash
cd backend
npm install
```

#### Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```env
# Server
PORT=3000
NODE_ENV=development

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=geosmart_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password

# AI Service
GEMINI_API_KEY=your_gemini_api_key_here

# File Upload
MAX_FILE_SIZE=5242880
UPLOAD_DIR=./uploads
```

#### Set Up Database

Make sure PostgreSQL is running, then:

```bash
npm run db:setup
```

This will:
- Create the `geosmart_db` database
- Run all migrations
- Set up tables and indexes
- Insert sample zone data

#### Start Backend Server
```bash
npm run dev
```

The backend should now be running on `http://localhost:3000`

---

### 3. Frontend Setup

Open a new terminal:

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Start Frontend Dev Server
```bash
npm run dev
```

The frontend should now be running on `http://localhost:5173`

---

## Verification

### Test Backend Health

```bash
curl http://localhost:3000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-21T...",
  "service": "GeoSmart Multi-Agent Backend"
}
```

### Test Frontend

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the GeoSmart interface with a map.

---

## Testing the Multi-Agent System

### 1. Submit a Test Complaint

1. Click on the map to select a location (around Hyderabad: lat ~17.43, lng ~78.40)
2. Enter complaint text: "Garbage pile near hospital for 3 days"
3. Click "Submit & Process with Multi-Agent AI"
4. Watch the agent execution timeline appear

### 2. Verify Agent Execution

You should see all 5 agents execute in sequence:
- 🧠 Understanding Agent
- 🗺️ GIS Intelligence Agent
- 🏷️ Classification Agent
- 🎯 Routing Agent
- 📋 Action Planning Agent

### 3. Check Database

```bash
# Connect to PostgreSQL
psql -U postgres -d geosmart_db

# View complaints
SELECT id, category, severity, department FROM complaints;

# View agent executions
SELECT agent_name, execution_time_ms, status FROM agent_executions ORDER BY created_at DESC LIMIT 10;

# Exit
\q
```

---

## Troubleshooting

### Database Connection Error

**Problem:** `ECONNREFUSED` error when starting backend

**Solution:**
1. Ensure PostgreSQL is running:
   ```bash
   # Windows (if installed as service)
   services.msc
   # Look for PostgreSQL service and start it
   
   # macOS
   brew services start postgresql@14
   
   # Linux
   sudo systemctl start postgresql
   ```
2. Verify your database credentials in `.env`
3. Test connection:
   ```bash
   psql -U postgres
   ```

### Gemini API Error

**Problem:** `API key not valid` error

**Solution:**
1. Get a valid API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Update `GEMINI_API_KEY` in `backend/.env`
3. Restart the backend server

### Frontend Cannot Connect to Backend

**Problem:** CORS error or network error

**Solution:**
1. Ensure backend is running on port 3000
2. Check `vite.config.js` proxy configuration
3. Clear browser cache and reload

### Map Not Loading

**Problem:** Blank map or tiles not loading

**Solution:**
1. Check internet connection (map tiles from OpenStreetMap)
2. Check browser console for errors
3. Ensure Leaflet CSS is loaded (check `index.html`)

---

## Development Tips

### Hot Reload

- **Backend:** Uses Node.js `--watch` flag (automatically reloads on file changes)
- **Frontend:** Vite hot module replacement (instant updates)

### Database Reset

If you need to reset the database:

```bash
cd backend

# Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS geosmart_db;"
npm run db:setup
```

### View Logs

**Backend logs:**
- Console output shows all API requests
- Agent execution logs show detailed agent flow

**Frontend logs:**
- Open browser DevTools (F12)
- Check Console tab for errors
- Network tab for API requests

---

## Production Deployment

### Backend

1. Set `NODE_ENV=production` in `.env`
2. Use a process manager like PM2:
   ```bash
   npm install -g pm2
   pm2 start server.js --name geosmart-backend
   ```
3. Set up PostgreSQL with proper credentials
4. Configure nginx as reverse proxy
5. Enable HTTPS with Let's Encrypt

### Frontend

1. Build production bundle:
   ```bash
   npm run build
   ```
2. Serve the `dist/` folder with nginx or similar
3. Update API endpoint in production config

---

## Next Steps

- ✅ Submit test complaints and watch multi-agent execution
- ✅ Explore the API with Postman or curl
- ✅ Check database to see agent execution traces
- ✅ Customize agents for your use case
- ✅ Add more zones/wards to GeoJSON data

For more information, see:
- [API Documentation](./API.md)
- [Architecture Documentation](./ARCHITECTURE.md)
- [Main README](../README.md)
