"""SQLite database layer using aiosqlite."""
import aiosqlite
from contextvars import ContextVar
from typing import Optional

DB_PATH = "coderresearch_v3.db"
db_connection: ContextVar[Optional[aiosqlite.Connection]] = ContextVar("db_connection", default=None)


async def get_db() -> aiosqlite.Connection:
    """获取数据库连接（每个上下文一个）"""
    conn = db_connection.get()
    if conn is None:
        conn = await aiosqlite.connect(DB_PATH)
        conn.row_factory = aiosqlite.Row
        db_connection.set(conn)
    return conn


async def init_db():
    """初始化数据库表结构"""
    conn = await get_db()
    
    # Codes 表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            definition TEXT DEFAULT '',
            level TEXT DEFAULT 'open',
            category_id TEXT,
            created_by TEXT DEFAULT 'human',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version TEXT DEFAULT '1.0'
        )
    """)
    
    # Categories 表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            definition TEXT DEFAULT '',
            parent_id TEXT,
            properties TEXT DEFAULT '[]',
            dimensions TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Sessions 表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Segments 表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS segments (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            source TEXT,
            position_start INTEGER,
            position_end INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    await conn.commit()
    print("[OK] Database initialized")


async def close_db():
    """关闭数据库连接"""
    conn = db_connection.get()
    if conn:
        await conn.close()
        db_connection.set(None)
