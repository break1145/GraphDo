# StoreDao.py
from typing import List

from backend.agent.models import Profile, ToDo, Instruction
from backend.utils.pg_pool import get_pg_pool, init_pg_pool



class StoreDao:
    def __init__(self):
        self.pool = init_pg_pool()

    async def get_profile_by_id(self, user_id: str) -> Profile:
        """
        根据id获取用户信息
        :param user_id:
        :return:
        """
        sql = f"""
            SELECT
                value ->> 'name' AS name,
                value ->> 'job' AS job,
                value ->> 'location' AS location,
                value ->> 'interests' AS interests
            FROM store
            WHERE prefix = 'profile.{user_id}';
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return Profile.from_dict(rows[0])

    async def get_todos_by_id(self, user_id: str) -> List[ToDo]:
        """
        根据id获取待办事项
        :param user_id:
        :return:
        """
        sql = f"""
            SELECT
                value ->> 'task' as task,
                value ->> 'status' as status,
                value ->> 'deadline' as deadline,
                value ->> 'solutions' as solutions,
                value ->> 'planned_edits' as planned_edits,
                value ->> 'time_to_complete' as time_to_complete
            FROM store
            WHERE prefix = 'todo.{user_id}';
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [ToDo.from_dict(row) for row in rows]

    async def get_instructions_by_id(self, user_id: str) -> List[Instruction]:
        sql = f"""
            SELECT
                value ->> 'content' as content,
                value ->> 'language' as language
            FROM store
            WHERE prefix = 'instructions.1';
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [Instruction.from_dict(row) for row in rows]






