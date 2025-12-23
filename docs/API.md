# API Documentation

## Base URL
```
http://localhost:3000/api
```

## Authentication
Currently, the API does not require authentication. For production deployment, implement JWT or OAuth 2.0.

---

## Endpoints

### 1. Create Complaint

**POST** `/api/complaints`

Submit a new complaint and trigger multi-agent processing.

#### Request Body
```json
{
  "text": "Garbage not collected for 3 days near Apollo Hospital",
  "latitude": 17.4326,
  "longitude": 78.4071,
  "address": "Road No 14, Banjara Hills (optional)"
}
```

#### Response (201 Created)
```json
{
  "success": true,
  "data": {
    "id": 123,
    "text": "Garbage not collected for 3 days near Apollo Hospital",
    "latitude": 17.4326,
    "longitude": 78.4071,
    "address": "Road No 14, Banjara Hills",
    "category": "Sanitation",
    "severity": "High",
    "department": "GHMC Sanitation",
    "zone_name": "Khairatabad Zone",
    "ward_number": 115,
    "ai_summary": "Garbage accumulation reported in Khairatabad Zone",
    "suggested_action": "Route to GHMC Sanitation team for Ward 115",
    "action_plan": {
      "immediate_actions": ["Alert sanitation supervisor", "Schedule emergency collection"],
      "timeline": "4 hours",
      "resources_needed": ["1 garbage truck", "2-3 workers"]
    },
    "status": "pending",
    "created_at": "2025-12-21T00:00:00.000Z",
    "agent_execution_summary": {
      "total_agents": 5,
      "execution_time_ms": 3450,
      "agents_executed": [
        {
          "name": "UnderstandingAgent",
          "status": "success",
          "execution_time_ms": 890,
          "key_findings": "Issue type: Garbage accumulation, Urgency: High"
        },
        {
          "name": "GISIntelligenceAgent",
          "status": "success",
          "execution_time_ms": 450,
          "key_findings": "Zone: Khairatabad, Ward: 115, Proximity: Apollo Hospital"
        }
        // ... more agents
      ]
    }
  }
}
```

---

### 2. List Complaints

**GET** `/api/complaints`

Fetch all complaints with optional filters.

#### Query Parameters
- `status` (optional): `pending`, `in-progress`, or `resolved`
- `severity` (optional): `Low`, `Medium`, or `High`
- `department` (optional): Department name (partial match)
- `limit` (optional): Number of results (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)

#### Example Request
```
GET /api/complaints?status=pending&severity=High&limit=10
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "text": "...",
      "category": "Sanitation",
      "severity": "High",
      "status": "pending",
      "created_at": "2025-12-21T00:00:00.000Z"
      // ... other fields
    }
  ],
  "total": 45,
  "limit": 10,
  "offset": 0
}
```

---

### 3. Get Single Complaint

**GET** `/api/complaints/:id`

Get detailed information about a specific complaint including agent execution history.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "id": 123,
    // ... complaint fields
    "agent_executions": [
      {
        "agent_name": "UnderstandingAgent",
        "execution_time_ms": 890,
        "status": "success",
        "output_data": { /* agent output */ },
        "created_at": "2025-12-21T00:00:00.000Z"
      }
      // ... more executions
    ]
  }
}
```

---

### 4. Update Complaint Status

**PATCH** `/api/complaints/:id`

Update the status of a complaint.

#### Request Body
```json
{
  "status": "in-progress"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "id": 123,
    "status": "in-progress",
    "updated_at": "2025-12-21T00:10:00.000Z"
    // ... other fields
  }
}
```

---

### 5. Get Statistics

**GET** `/api/stats`

Get system-wide statistics and insights.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_complaints": 150,
      "pending": 45,
      "in_progress": 30,
      "resolved": 75,
      "high_severity": 25,
      "medium_severity": 80,
      "low_severity": 45
    },
    "by_category": [
      { "category": "Sanitation", "count": 60 },
      { "category": "Roads", "count": 45 },
      { "category": "Streetlights", "count": 25 }
    ]
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "errors": [
    {
      "field": "latitude",
      "message": "Invalid latitude"
    }
  ]
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Complaint not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "Detailed error message (dev mode only)"
}
```

---

## Rate Limiting

Currently not implemented. For production, consider:
- Rate limit: 100 requests per 15 minutes per IP
- Burst limit: 10 requests per second

---

## CORS

The API allows cross-origin requests from any origin in development. For production, configure specific origins in `backend/server.js`.
