from litestar import Controller, get, post, put, delete
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK
from pydantic import BaseModel, field_validator
from typing import List, Optional
import traceback

from backend.dao.InstructionDao import InstructionDao
from backend.dao.ProfileDao import ProfileDao
from backend.dao.ToDoDao import ToDoDao
from backend.agent.models import Instruction, Profile, ToDo


class InstructionCreateRequest(BaseModel):
    user_id: str
    language: str
    content: str
    
    @field_validator("user_id", "language", "content")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("不能为空或仅包含空格")
        return v.strip()


class InstructionUpdateRequest(BaseModel):
    language: str
    content: str
    
    @field_validator("language", "content")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("不能为空或仅包含空格")
        return v.strip()


class ProfileCreateRequest(BaseModel):
    user_id: str
    name: Optional[str] = None
    location: Optional[str] = None
    job: Optional[str] = None
    connections: List[str] = []
    interests: List[str] = []
    
    @field_validator("user_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("user_id不能为空")
        return v.strip()


class TodoCreateRequest(BaseModel):
    user_id: str
    task: str
    time_to_complete: Optional[int] = None
    deadline: Optional[str] = None
    solutions: List[str] = []
    status: str = "not started"
    planned_edits: List[str] = []
    
    @field_validator("user_id", "task")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("不能为空或仅包含空格")
        return v.strip()


class CommonController(Controller):
    path = "/api"
    dependencies = {
        "instruction_dao": Provide(lambda: InstructionDao(), sync_to_thread=True),
        "profile_dao": Provide(lambda: ProfileDao(), sync_to_thread=True),
        "todo_dao": Provide(lambda: ToDoDao(), sync_to_thread=True)
    }

    # ==================== Instruction CRUD ====================
    
    @get("/instructions/{user_id:str}")
    async def get_instructions(self, user_id: str, instruction_dao: InstructionDao) -> dict:
        """
        获取用户的所有指令
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        try:
            instructions = await instruction_dao.get_by_id(user_id)
            return {
                "success": True,
                "response": [instruction.model_dump() for instruction in instructions]
            }
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    @post("/instructions")
    async def create_instruction(self, data: InstructionCreateRequest, instruction_dao: InstructionDao) -> dict:
        """
        创建新的用户指令
        """
        try:
            instruction = Instruction(
                language=data.language,
                content=data.content
            )
            success = await instruction_dao.create_instruction(data.user_id, instruction)
            
            if success:
                return {"success": True, "message": "指令创建成功"}
            else:
                return {"error": "指令创建失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    @put("/instructions/{user_id:str}/{key:str}")
    async def update_instruction(self, user_id: str, key: str, data: InstructionUpdateRequest, instruction_dao: InstructionDao) -> dict:
        """
        更新指定的用户指令
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        if not key or not key.strip():
            return {"error": "key不能为空"}
        
        try:
            instruction = Instruction(
                language=data.language,
                content=data.content
            )
            success = await instruction_dao.update_by_key(user_id, key, instruction)
            
            if success:
                return {"success": True, "message": "指令更新成功"}
            else:
                return {"error": "指令更新失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    @delete("/instructions/{user_id:str}/{key:str}", status_code=HTTP_200_OK)
    async def delete_instruction(self, user_id: str, key: str, instruction_dao: InstructionDao) -> dict:
        """
        删除指定的用户指令
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        if not key or not key.strip():
            return {"error": "key不能为空"}
        
        try:
            success = await instruction_dao.delete_by_key(user_id, key)
            
            if success:
                return {"success": True, "message": "指令删除成功"}
            else:
                return {"error": "指令删除失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    # ==================== Profile CRUD ====================
    
    @get("/profile/{user_id:str}")
    async def get_profile(self, user_id: str, profile_dao: ProfileDao) -> dict:
        """
        获取用户档案
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        try:
            profile = await profile_dao.get_by_id(user_id)
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
    
    @post("/profile")
    async def create_profile(self, data: ProfileCreateRequest, profile_dao: ProfileDao) -> dict:
        """
        创建用户档案
        """
        try:
            profile = Profile(
                name=data.name,
                location=data.location,
                job=data.job,
                connections=data.connections,
                interests=data.interests
            )
            success = await profile_dao.create_profile(data.user_id, profile)
            
            if success:
                return {"success": True, "message": "用户档案创建成功"}
            else:
                return {"error": "用户档案创建失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    @put("/profile/{user_id:str}")
    async def update_profile(self, user_id: str, data: ProfileCreateRequest, profile_dao: ProfileDao) -> dict:
        """
        更新用户档案
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        try:
            profile = Profile(
                name=data.name,
                location=data.location,
                job=data.job,
                connections=data.connections,
                interests=data.interests
            )
            success = await profile_dao.update_profile(user_id, profile)
            
            if success:
                return {"success": True, "message": "用户档案更新成功"}
            else:
                return {"error": "用户档案更新失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    # ==================== To do CRUD ====================
    
    @get("/todos/{user_id:str}")
    async def get_todos(self, user_id: str, todo_dao: ToDoDao) -> dict:
        """
        获取用户的所有待办事项
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        try:
            todos = await todo_dao.get_by_id(user_id)
            return {
                "success": True,
                "response": [todo.model_dump() for todo in todos]
            }
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    @post("/todos")
    async def create_todo(self, data: TodoCreateRequest, todo_dao: ToDoDao) -> dict:
        """
        创建新的待办事项
        """
        try:
            todo = ToDo(
                task=data.task,
                time_to_complete=data.time_to_complete,
                deadline=data.deadline,
                solutions=data.solutions,
                status=data.status,
                planned_edits=data.planned_edits
            )
            success = await todo_dao.create_todo(data.user_id, todo)
            
            if success:
                return {"success": True, "message": "待办事项创建成功"}
            else:
                return {"error": "待办事项创建失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    @put("/todos/{user_id:str}/{key:str}")
    async def update_todo(self, user_id: str, key: str, data: TodoCreateRequest, todo_dao: ToDoDao) -> dict:
        """
        更新指定的待办事项
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        if not key or not key.strip():
            return {"error": "key不能为空"}
        
        try:
            todo = ToDo(
                task=data.task,
                time_to_complete=data.time_to_complete,
                deadline=data.deadline,
                solutions=data.solutions,
                status=data.status,
                planned_edits=data.planned_edits,
                key = key
            )
            success = await todo_dao.update_by_key(user_id, key, todo)
            
            if success:
                return {"success": True, "message": "待办事项更新成功"}
            else:
                return {"error": "待办事项更新失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
    
    @delete("/todos/{user_id:str}/{key:str}", status_code=HTTP_200_OK)
    async def delete_todo(self, user_id: str, key: str, todo_dao: ToDoDao) -> dict:
        """
        删除指定的待办事项
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        if not key or not key.strip():
            return {"error": "key不能为空"}
        
        try:
            success = await todo_dao.delete_by_key(user_id, key)
            
            if success:
                return {"success": True, "message": "待办事项删除成功"}
            else:
                return {"error": "待办事项删除失败"}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}