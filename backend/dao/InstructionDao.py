import json
from typing import List
from backend.dao.BaseDao import BaseDao
from backend.agent.models import Instruction

class InstructionDao(BaseDao[Instruction]):
    """用户偏好说明数据访问对象"""
    
    async def get_by_id(self, user_id: str) -> List[Instruction]:
        """
        根据用户ID获取用户偏好说明
        :param user_id: 用户ID
        :return: Instruction对象列表
        """
        sql = """
            SELECT
                value ->> 'content' as content,
                value ->> 'language' as language,
                key
            FROM store
            WHERE prefix = %s;
        """
        
        try:
            rows = self._execute_query(sql, (f'instructions.{user_id}',))
            return [Instruction.from_dict(row) for row in rows]
        except Exception as e:
            print(f"[InstructionDao] 查询用户偏好说明失败: {e}")
            return []

    
    async def create_instruction(self, user_id: str, instruction: Instruction) -> bool:
        """
        创建用户偏好说明
        :param user_id: 用户ID
        :param instruction: Instruction对象
        :return: 是否创建成功
        """
        sql = """
            INSERT INTO store (prefix, key, value)
            VALUES (%s, %s, %s)
            ON CONFLICT (prefix, key) DO UPDATE SET value = EXCLUDED.value;
        """
        
        try:
            instruction_data = instruction.model_dump(exclude_none=True)
            key = f"{user_id}_{instruction.language}"
            self._execute_write(sql, (f'instructions.{user_id}', key, json.dumps(instruction_data)))
            return True
        except Exception as e:
            print(f"[InstructionDao] 创建偏好说明失败: {e}")
            return False

    async def delete_by_key(self, user_id: str, key: str) -> bool:
        """
        根据key删除用户偏好说明
        :param user_id: 用户ID
        :param key: 记录的key
        :return: 是否删除成功
        """
        sql = """
            DELETE FROM store 
            WHERE prefix = %s AND key = %s;
        """
        
        try:
            self._execute_write(sql, (f'instructions.{user_id}', key))
            return True
        except Exception as e:
            print(f"[InstructionDao] 删除偏好说明失败: {e}")
            return False
    
    async def update_by_key(self, user_id: str, key: str, instruction: Instruction) -> bool:
        """
        根据key更新用户偏好说明
        :param user_id: 用户ID
        :param key: 记录的key
        :param instruction: Instruction对象
        :return: 是否更新成功
        """
        sql = """
            UPDATE store 
            SET value = %s 
            WHERE prefix = %s AND key = %s;
        """
        
        try:
            instruction_data = instruction.model_dump(exclude_none=True)
            self._execute_write(sql, (json.dumps(instruction_data), f'instructions.{user_id}', key))
            return True
        except Exception as e:
            print(f"[InstructionDao] 更新偏好说明失败: {e}")
            return False