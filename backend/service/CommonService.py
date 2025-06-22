from typing import List, Optional
from backend.dao.InstructionDao import InstructionDao
from backend.dao.ProfileDao import ProfileDao
from backend.dao.ToDoDao import ToDoDao
from backend.agent.models import Instruction, Profile, ToDo
import traceback


class CommonService:
    
    def __init__(self):
        self.instruction_dao = InstructionDao()
        self.profile_dao = ProfileDao()
        self.todo_dao = ToDoDao()
    
    # ==================== Instruction 业务逻辑 ====================
    
    async def get_instructions(self, user_id: str) -> dict:
        """
        获取用户的所有指令
        """
        try:
            instructions = await self.instruction_dao.get_by_id(user_id)
            return {
                "success": True,
                "response": [instruction.model_dump() for instruction in instructions]
            }
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    async def create_instruction(self, user_id: str, language: str, content: str) -> dict:
        """
        创建新的用户指令
        """
        try:
            instruction = Instruction(
                language=language,
                content=content
            )
            success = await self.instruction_dao.create_instruction(user_id, instruction)
            
            if success:
                return {"success": True, "message": "指令创建成功"}
            else:
                return {"error": "指令创建失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    async def update_instruction(self, user_id: str, key: str, language: str, content: str) -> dict:
        """
        更新指定的用户指令
        """
        try:
            instruction = Instruction(
                language=language,
                content=content
            )
            success = await self.instruction_dao.update_by_key(user_id, key, instruction)
            
            if success:
                return {"success": True, "message": "指令更新成功"}
            else:
                return {"error": "指令更新失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    async def delete_instruction(self, user_id: str, key: str) -> dict:
        """
        删除指定的用户指令
        """
        try:
            success = await self.instruction_dao.delete_by_key(user_id, key)
            
            if success:
                return {"success": True, "message": "指令删除成功"}
            else:
                return {"error": "指令删除失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    # ==================== Profile 业务逻辑 ====================
    
    async def get_profile(self, user_id: str) -> dict:
        """
        获取用户档案
        """
        try:
            profile = await self.profile_dao.get_by_id(user_id)
            if profile:
                return {
                    "success": True,
                    "response": profile.model_dump()
                }
            else:
                return {"error": "用户档案不存在"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    async def create_profile(self, user_id: str, name: Optional[str] = None, 
                           location: Optional[str] = None, job: Optional[str] = None,
                           connections: List[str] = None, interests: List[str] = None) -> dict:
        """
        创建用户档案
        """
        try:
            profile = Profile(
                name=name,
                location=location,
                job=job,
                connections=connections or [],
                interests=interests or []
            )
            success = await self.profile_dao.create_profile(user_id, profile)
            
            if success:
                return {"success": True, "message": "用户档案创建成功"}
            else:
                return {"error": "用户档案创建失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    async def update_profile(self, user_id: str, name: Optional[str] = None,
                           location: Optional[str] = None, job: Optional[str] = None,
                           connections: List[str] = None, interests: List[str] = None) -> dict:
        """
        更新用户档案
        """
        try:
            profile = Profile(
                name=name,
                location=location,
                job=job,
                connections=connections or [],
                interests=interests or []
            )
            success = await self.profile_dao.update_profile(user_id, profile)
            
            if success:
                return {"success": True, "message": "用户档案更新成功"}
            else:
                return {"error": "用户档案更新失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    # ==================== Todo 业务逻辑 ====================
    
    async def get_todos(self, user_id: str) -> dict:
        """
        获取用户的所有待办事项
        """
        try:
            todos = await self.todo_dao.get_by_id(user_id)
            return {
                "success": True,
                "response": [todo.model_dump() for todo in todos]
            }
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    async def create_todo(self, user_id: str, task: str, time_to_complete: Optional[int] = None,
                         deadline: Optional[str] = None, solutions: List[str] = None,
                         status: str = "not started", planned_edits: List[str] = None) -> dict:
        """
        创建新的待办事项
        """
        try:
            todo = ToDo(
                task=task,
                time_to_complete=time_to_complete,
                deadline=deadline,
                solutions=solutions or [],
                status=status,
                planned_edits=planned_edits or []
            )
            success = await self.todo_dao.create_todo(user_id, todo)
            
            if success:
                return {"success": True, "message": "待办事项创建成功"}
            else:
                return {"error": "待办事项创建失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    async def update_todo(self, user_id: str, key: str, task: str, 
                         time_to_complete: Optional[int] = None, deadline: Optional[str] = None,
                         solutions: List[str] = None, status: str = "not started",
                         planned_edits: List[str] = None) -> dict:
        """
        更新指定的待办事项
        """
        try:
            todo = ToDo(
                key=key,
                task=task,
                time_to_complete=time_to_complete,
                deadline=deadline,
                solutions=solutions or [],
                status=status,
                planned_edits=planned_edits or []
            )
            success = await self.todo_dao.update_by_key(user_id, key, todo)
            
            if success:
                return {"success": True, "message": "待办事项更新成功"}
            else:
                return {"error": "待办事项更新失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    async def delete_todo(self, user_id: str, key: str) -> dict:
        """
        删除指定的待办事项
        """
        try:
            success = await self.todo_dao.delete_by_key(user_id, key)
            
            if success:
                return {"success": True, "message": "待办事项删除成功"}
            else:
                return {"error": "待办事项删除失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}