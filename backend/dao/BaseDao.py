from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List
from backend.utils.pg_pool import get_pg_pool, init_pg_pool
from psycopg_pool import ConnectionPool
import json

T = TypeVar('T')

class BaseDao(ABC, Generic[T]):
    """DAO基类，提供通用的数据库操作方法"""
    
    def __init__(self):
        self.pool: ConnectionPool = init_pg_pool()
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> T | List[T]:
        """根据用户ID获取数据的抽象方法"""
        pass
    
    def _execute_query(self, sql: str, params: tuple = None):
        """执行SQL查询的通用方法"""
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                return cur.fetchall()

    def _execute_write(self, sql: str, params: tuple = None):
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()

    def _execute_single_query(self, sql: str, params: tuple = None):
        """执行单条记录查询的通用方法"""
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                if params:
                    # 处理字典类型参数，转换为JSON字符串
                    processed_params = []
                    for param in params:
                        if isinstance(param, dict):
                            processed_params.append(json.dumps(param))
                        else:
                            processed_params.append(param)
                    cur.execute(sql, tuple(processed_params))
                else:
                    cur.execute(sql)
                return cur.fetchone()