from litestar import Controller, get, post, put, delete
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK
from pydantic import BaseModel, field_validator
from typing import List, Optional

from backend.service.CommonService import CommonService


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
        "common_service": Provide(lambda: CommonService(), sync_to_thread=True)
    }

    # ==================== Instruction CRUD ====================
    
    @get("/instructions/{user_id:str}")
    async def get_instructions(self, user_id: str, common_service: CommonService) -> dict:
        """
        获取用户的所有指令
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        return await common_service.get_instructions(user_id)
    
    @post("/instructions")
    async def create_instruction(self, data: InstructionCreateRequest, common_service: CommonService) -> dict:
        """
        创建新的用户指令
        """
        return await common_service.create_instruction(
            user_id=data.user_id,
            language=data.language,
            content=data.content
        )
    
    @put("/instructions/{user_id:str}/{key:str}")
    async def update_instruction(self, user_id: str, key: str, data: InstructionUpdateRequest, common_service: CommonService) -> dict:
        """
        更新指定的用户指令
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        if not key or not key.strip():
            return {"error": "key不能为空"}
        
        return await common_service.update_instruction(
            user_id=user_id,
            key=key,
            language=data.language,
            content=data.content
        )
    
    @delete("/instructions/{user_id:str}/{key:str}", status_code=HTTP_200_OK)
    async def delete_instruction(self, user_id: str, key: str, common_service: CommonService) -> dict:
        """
        删除指定的用户指令
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        if not key or not key.strip():
            return {"error": "key不能为空"}
        
        return await common_service.delete_instruction(user_id, key)

    # ==================== Profile CRUD ====================
    
    @get("/profile/{user_id:str}")
    async def get_profile(self, user_id: str, common_service: CommonService) -> dict:
        """
        获取用户档案
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        return await common_service.get_profile(user_id)
    
    @post("/profile")
    async def create_profile(self, data: ProfileCreateRequest, common_service: CommonService) -> dict:
        """
        创建用户档案
        """
        return await common_service.create_profile(
            user_id=data.user_id,
            name=data.name,
            location=data.location,
            job=data.job,
            connections=data.connections,
            interests=data.interests
        )
    
    @put("/profile/{user_id:str}")
    async def update_profile(self, user_id: str, data: ProfileCreateRequest, common_service: CommonService) -> dict:
        """
        更新用户档案
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        return await common_service.update_profile(
            user_id=user_id,
            name=data.name,
            location=data.location,
            job=data.job,
            connections=data.connections,
            interests=data.interests
        )

    # ==================== Todo CRUD ====================
    
    @get("/todos/{user_id:str}")
    async def get_todos(self, user_id: str, common_service: CommonService) -> dict:
        """
        获取用户的所有待办事项
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        return await common_service.get_todos(user_id)
    
    @post("/todos")
    async def create_todo(self, data: TodoCreateRequest, common_service: CommonService) -> dict:
        """
        创建新的待办事项
        """
        return await common_service.create_todo(
            user_id=data.user_id,
            task=data.task,
            time_to_complete=data.time_to_complete,
            deadline=data.deadline,
            solutions=data.solutions,
            status=data.status,
            planned_edits=data.planned_edits
        )
    
    @put("/todos/{user_id:str}/{key:str}")
    async def update_todo(self, user_id: str, key: str, data: TodoCreateRequest, common_service: CommonService) -> dict:
        """
        更新指定的待办事项
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        if not key or not key.strip():
            return {"error": "key不能为空"}
        
        return await common_service.update_todo(
            user_id=user_id,
            key=key,
            task=data.task,
            time_to_complete=data.time_to_complete,
            deadline=data.deadline,
            solutions=data.solutions,
            status=data.status,
            planned_edits=data.planned_edits
        )
    
    @delete("/todos/{user_id:str}/{key:str}", status_code=HTTP_200_OK)
    async def delete_todo(self, user_id: str, key: str, common_service: CommonService) -> dict:
        """
        删除指定的待办事项
        """
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        if not key or not key.strip():
            return {"error": "key不能为空"}
        
        return await common_service.delete_todo(user_id, key)