import json
from typing import List
from backend.dao.BaseDao import BaseDao
from backend.agent.models import ToDo

class ToDoDao(BaseDao[ToDo]):
    """待办事项数据访问对象"""
    
    async def get_by_id(self, user_id: str) -> List[ToDo]:
        """
        根据用户ID获取所有待办事项
        :param user_id: 用户ID
        :return: ToDo对象列表
        """
        sql = """
            SELECT
                value ->> 'task' as task,
                value ->> 'status' as status,
                value ->> 'deadline' as deadline,
                value ->> 'solutions' as solutions,
                value ->> 'planned_edits' as planned_edits,
                value ->> 'time_to_complete' as time_to_complete
            FROM store
            WHERE prefix = %s;
        """
        
        try:
            rows = self._execute_query(sql, (f'todo.{user_id}',))
            return [ToDo.from_dict(row) for row in rows]
        except Exception as e:
            print(f"[ToDoDao] 查询待办事项失败: {e}")
            return []

    
    async def create_todo(self, user_id: str, todo: ToDo) -> bool:
        """
        创建待办事项
        :param user_id: 用户ID
        :param to do: To Do对象
        :return: 是否创建成功
        """
        sql = """
            INSERT INTO store (prefix, key, value)
            VALUES (%s, %s, %s);
        """
        
        try:
            todo_data = todo.model_dump(exclude_none=True)
            key = f"{user_id}_{todo.task[:50]}"
            self._execute_write(sql, (f'todo.{user_id}', key, json.dumps(todo_data, default=str)))
            return True
        except Exception as e:
            print(f"[ToDoDao] 创建待办事项失败: {e}")
            return False

    async def delete_by_key(self, user_id: str, key: str) -> bool:
        """
        根据key删除待办事项
        :param user_id: 用户ID
        :param key: 记录的key
        :return: 是否删除成功
        """
        sql = """
            DELETE FROM store 
            WHERE prefix = %s AND key = %s;
        """
        
        try:
            self._execute_write(sql, (f'todo.{user_id}', key))
            return True
        except Exception as e:
            print(f"[ToDoDao] 删除待办事项失败: {e}")
            return False
    
    async def update_by_key(self, user_id: str, key: str, todo: ToDo) -> bool:
        """
        根据key更新待办事项
        :param user_id: 用户ID
        :param key: 记录的key
        :param todo: ToDo对象
        :return: 是否更新成功
        """
        sql = """
            UPDATE store 
            SET value = %s 
            WHERE prefix = %s AND key = %s;
        """
        
        try:
            todo_data = todo.model_dump(exclude_none=True)
            self._execute_write(sql, (json.dumps(todo_data, default=str), f'todo.{user_id}', key))
            return True
        except Exception as e:
            print(f"[ToDoDao] 更新待办事项失败: {e}")
            return False