import os
import shutil
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from pydantic import BaseModel, Field
import json
import asyncpg

from ..db.connection import db_connection
from ..agents.coordinator import CoordinatorAgent

router = APIRouter()

# Response Wrapper
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    total: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

# ----------------------------------------------------------------------
# Helper: Save Upload
# ----------------------------------------------------------------------
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload(file: UploadFile) -> str:
    # Sanitize filename (basic)
    filename = f"{int(time.time())}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/uploads/{filename}"

import time

# ----------------------------------------------------------------------
# POST /complaints
# ----------------------------------------------------------------------
@router.post("/complaints", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    text: str = Form(..., min_length=10),
    latitude: float = Form(..., ge=-90, le=90),
    longitude: float = Form(..., ge=-180, le=180),
    address: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    conn: asyncpg.Connection = Depends(db_connection),
):
    try:
        image_url = None
        if image:
            image_url = await save_upload(image)
            
        # Insert initial complaint
        complaint_id = await conn.fetchval(
            """
            INSERT INTO complaints (text, latitude, longitude, address, status, image_url)
            VALUES ($1, $2, $3, $4, 'pending', $5)
            RETURNING id
            """,
            text, latitude, longitude, address, image_url
        )
        
        # Trigger Multi-Agent
        coordinator = CoordinatorAgent()
        # Note: Coordinator expects a dict, not a pydantic model
        complaint_data = {
            "id": complaint_id,
            "text": text,
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "image_url": image_url, # Key used in coordinator
            "imageUrl": image_url   # Redundancy for agents that might look for this
        }
        
        processing_result = await coordinator.process_complaint(complaint_data)
        context_data = processing_result["result"]
        
        # Update Database with results
        # Mapping context fields to DB columns
        await conn.execute(
            """
            UPDATE complaints 
            SET category = $1, severity = $2, department = $3,
                zone_name = $4, ward_number = $5, ai_summary = $6,
                suggested_action = $7, action_plan = $8, updated_at = NOW()
            WHERE id = $9
            """,
            context_data.get('category'),
            context_data.get('severity'),
            context_data.get('department'),
            context_data.get('zone_name'),
            context_data.get('ward_number'),
            f"{context_data.get('issue_type') or 'Complaint'} reported in {context_data.get('zone_name') or 'area'}",
            context_data.get('routing_reasoning') or f"Route to {context_data.get('department')}",
            json.dumps(context_data.get('action_plan')),
            complaint_id
        )
        
        # Fetch complete record
        row = await conn.fetchrow("SELECT * FROM complaints WHERE id = $1", complaint_id)
        
        # Convert row to dict and add execution summary
        response_data = dict(row)
        response_data['agent_execution_summary'] = {
            "total_agents": len(processing_result['execution_log']),
            "execution_time_ms": processing_result['total_execution_time_ms'],
            "agents_executed": processing_result['execution_log']
        }
        
        return APIResponse(success=True, data=response_data)
        
    except Exception as e:
        print(f"Error processing complaint: {e}")
        return APIResponse(success=False, error="Failed to process complaint", message=str(e))

# ----------------------------------------------------------------------
# GET /complaints
# ----------------------------------------------------------------------
@router.get("/complaints", response_model=APIResponse)
async def list_complaints(
    status: Optional[str] = Query(None, regex="^(pending|in-progress|resolved)$"),
    severity: Optional[str] = Query(None, regex="^(Low|Medium|High)$"),
    department: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    conn: asyncpg.Connection = Depends(db_connection),
):
    try:
        where = ["1=1"]
        params = []
        
        if status:
            params.append(status)
            where.append(f"status = ${len(params)}")
        if severity:
            params.append(severity)
            where.append(f"severity = ${len(params)}")
        if department:
            params.append(f"%{department}%")
            where.append(f"department ILIKE ${len(params)}")
            
        where_clause = " AND ".join(where)
        
        # Get Data
        rows = await conn.fetch(
            f"SELECT * FROM complaints WHERE {where_clause} ORDER BY created_at DESC LIMIT ${len(params)+1} OFFSET ${len(params)+2}",
            *params, limit, offset
        )
        
        # Get Total
        total = await conn.fetchval(
            f"SELECT COUNT(*) FROM complaints WHERE {where_clause}",
            *params
        )
        
        return APIResponse(
            success=True,
            data=[dict(r) for r in rows],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        print(f"Error fetching complaints: {e}")
        return APIResponse(success=False, error="Failed to fetch complaints", message=str(e))

# ----------------------------------------------------------------------
# GET /complaints/{id}
# ----------------------------------------------------------------------
@router.get("/complaints/{id}", response_model=APIResponse)
async def get_complaint(
    id: int,
    conn: asyncpg.Connection = Depends(db_connection),
):
    try:
        row = await conn.fetchrow("SELECT * FROM complaints WHERE id = $1", id)
        if not row:
            return APIResponse(success=False, error="Complaint not found")
            
        executions = await conn.fetch(
            """
            SELECT agent_name, execution_time_ms, status, output_data, created_at 
            FROM agent_executions 
            WHERE complaint_id = $1 
            ORDER BY created_at ASC
            """,
            id
        )
        
        data = dict(row)
        data['agent_executions'] = [dict(r) for r in executions]
        
        return APIResponse(success=True, data=data)
        
    except Exception as e:
        return APIResponse(success=False, error="Failed to fetch complaint", message=str(e))

# ----------------------------------------------------------------------
# PATCH /complaints/{id}
# ----------------------------------------------------------------------
class UpdateStatus(BaseModel):
    status: str = Field(..., pattern="^(pending|in-progress|resolved)$")

@router.patch("/complaints/{id}", response_model=APIResponse)
async def update_complaint(
    id: int,
    body: UpdateStatus,
    conn: asyncpg.Connection = Depends(db_connection),
):
    try:
        row = await conn.fetchrow(
            "UPDATE complaints SET status = $1, updated_at = NOW() WHERE id = $2 RETURNING *",
            body.status, id
        )
        
        if not row:
            return APIResponse(success=False, error="Complaint not found")
            
        return APIResponse(success=True, data=dict(row))
        
    except Exception as e:
        return APIResponse(success=False, error="Failed to update complaint", message=str(e))

# ----------------------------------------------------------------------
# GET /stats
# ----------------------------------------------------------------------
@router.get("/stats", response_model=APIResponse)
async def get_stats(conn: asyncpg.Connection = Depends(db_connection)):
    try:
        stats = await conn.fetchrow("""
          SELECT 
            COUNT(*) as total_complaints,
            COUNT(*) FILTER (WHERE status = 'pending') as pending,
            COUNT(*) FILTER (WHERE status = 'in-progress') as in_progress,
            COUNT(*) FILTER (WHERE status = 'resolved') as resolved,
            COUNT(*) FILTER (WHERE severity = 'High') as high_severity,
            COUNT(*) FILTER (WHERE severity = 'Medium') as medium_severity,
            COUNT(*) FILTER (WHERE severity = 'Low') as low_severity
          FROM complaints
        """)
        
        cat_stats = await conn.fetch("""
          SELECT category, COUNT(*) as count 
          FROM complaints 
          WHERE category IS NOT NULL
          GROUP BY category 
          ORDER BY count DESC
        """)
        
        return APIResponse(success=True, data={
            "overview": dict(stats),
            "by_category": [dict(r) for r in cat_stats]
        })
        
    except Exception as e:
        return APIResponse(success=False, error="Failed to fetch statistics", message=str(e))
