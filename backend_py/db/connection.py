import os
import asyncpg
from typing import AsyncGenerator

_pool: asyncpg.Pool | None = None

async def init_pool() -> None:
    """Create a global asyncpg connection pool."""
    global _pool
    if _pool is None:
        try:
           
            dsn = f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'geosmart_db')}"
            _pool = await asyncpg.create_pool(
                dsn=dsn,
                min_size=1,
                max_size=10,
            )
        except Exception as e:
            print(f"Failed to connect to DB: {e}")
            raise

async def close_pool() -> None:
    """Close the global pool (called on shutdown)."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

async def get_pool() -> asyncpg.Pool:
    """Return the global pool, initializing it if needed."""
    if _pool is None:
        await init_pool()
    return _pool

# Dependency for FastAPI routes
async def db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn
