import json
from typing import Optional
from backend.dao.BaseDao import BaseDao
from backend.agent.models import Profile

class ProfileDao(BaseDao[Profile]):
    """用户档案数据访问对象"""
    
    async def get_by_id(self, user_id: str) -> Optional[Profile]:
        """
        根据用户ID获取用户档案信息
        :param user_id: 用户ID
        :return: Profile对象或None
        """
        sql = """
            SELECT
                value ->> 'name' AS name,
                value ->> 'job' AS job,
                value ->> 'location' AS location,
                value ->> 'interests' AS interests,
                value ->> 'connections' AS connections
            FROM store
            WHERE prefix = %s;
        """
        
        try:
            row = self._execute_single_query(sql, (f'profile.{user_id}',))
            if row:
                return Profile.from_dict(row)
            return None
        except Exception as e:
            print(f"[ProfileDao] 查询用户档案失败: {e}")
            return None
    
    async def create_profile(self, user_id: str, profile: Profile) -> bool:
        """
        创建用户档案
        :param user_id: 用户ID
        :param profile: Profile对象
        :return: 是否创建成功
        """
        sql = """
            INSERT INTO store (prefix, key, value)
            VALUES (%s, %s, %s)
            ON CONFLICT (prefix, key) DO UPDATE SET value = EXCLUDED.value;
        """
        
        try:
            profile_data = profile.model_dump(exclude_none=True)
            self._execute_write(sql, (f'profile.{user_id}', user_id, json.dumps(profile_data)))
            return True
        except Exception as e:
            print(f"[ProfileDao] 创建用户档案失败: {e}")
            return False

    async def update_profile(self, user_id: str, profile: Profile) -> bool:
        sql = """
            UPDATE store 
            SET value = %s 
            WHERE prefix = %s;
        """
        try:
            profile_data = profile.model_dump(exclude_none=True)
            self._execute_write(sql, (json.dumps(profile_data), f'profile.{user_id}'))
            return True
        except Exception as e:
            print(f"[ProfileDao] 更新用户档案失败: {e}")
            return False