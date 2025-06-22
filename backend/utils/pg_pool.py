import os

from litestar.config.app import AppConfig
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from dotenv import load_dotenv

_pool: ConnectionPool | None = None

def init_pg_pool() -> ConnectionPool:
    """初始化 PostgreSQL 连接池"""
    global _pool
    load_dotenv()
    db_uri = os.getenv("DB_URI")
    if not db_uri:
        raise RuntimeError("未配置环境变量 DB_URI")

    _pool = ConnectionPool(
        conninfo=db_uri,
        kwargs={
            "row_factory": dict_row,
            "autocommit": True
        }
    )
    print("[PG Pool] 初始化成功")
    return _pool

def on_startup_pg_pool(app_config: AppConfig) -> AppConfig:
    init_pg_pool()
    return app_config

def get_pg_pool() -> ConnectionPool:
    """获取连接池实例"""
    if _pool is None:
        raise RuntimeError("连接池未初始化，请在应用启动时调用 init_pg_pool()")
    return _pool

def close_pg_pool() -> None:
    """关闭连接池"""
    global _pool
    if _pool is not None:
        _pool.close()
        print("[PG Pool] 已关闭连接池")
