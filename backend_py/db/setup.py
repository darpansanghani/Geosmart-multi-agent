import asyncio
import os
from dotenv import load_dotenv


env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
print("ENV PATH:", env_path)
print("ENV EXISTS:", os.path.exists(env_path))
print("DOTENV LOADED:", load_dotenv(env_path, override=True))

from dotenv import dotenv_values
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / ".env"
config = dotenv_values(env_path)

required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]

missing = [k for k in required if not config.get(k)]
if missing:
    raise RuntimeError(f"Missing env vars: {missing}")



# Load env vars manually for standalone execution
# load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from backend_py.db.connection import init_pool, close_pool, get_pool

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS complaints (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    address TEXT,
    category TEXT,
    severity TEXT,
    department TEXT,
    zone_name TEXT,
    ward_number INTEGER,
    ai_summary TEXT,
    suggested_action TEXT,
    action_plan JSONB,
    status TEXT DEFAULT 'pending',
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_executions (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES complaints(id),
    agent_name TEXT NOT NULL,
    input_data JSONB,
    output_data JSONB,
    execution_time_ms INTEGER,
    status TEXT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_context (
    id SERIAL PRIMARY KEY,
    complaint_id INTEGER REFERENCES complaints(id),
    context_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

async def run_setup():
    print("Initializing database...")
    try:
        print("DB_HOST:", os.getenv("DB_HOST"))
        print("DB_PORT:", os.getenv("DB_PORT"))
        print("DB_NAME:", os.getenv("DB_NAME"))
        print("DB_USER:", os.getenv("DB_USER"))

        await init_pool()
        print(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
        pool = await get_pool()
        print("✅ Database connection pool created.")
        async with pool.acquire() as conn:
            await conn.execute(SCHEMA_SQL)
        print("✅ Database schema created/updated.")
    except Exception as e:
        print(f"Error setting up database: {e}")
    finally:
        await close_pool()

if __name__ == "__main__":
    asyncio.run(run_setup())
