from litestar import Litestar, get, post, Controller
from litestar.di import Provide
from pydantic import BaseModel, field_validator
from litestar.connection import Request
from litestar.response import ServerSentEvent
from backend.service.AgentService import AgentService
import traceback
import json


class ChatInput(BaseModel):
    user_id: str
    input: str
    @field_validator("user_id", "input")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("不能为空或仅包含空格")
        return v.strip()

class AgentChatController(Controller):
    path = "/agent"
    dependencies = {
        "agent_service": Provide(lambda: AgentService(), sync_to_thread=True)
    }

    @post("/chat")
    async def chat_with_agent(self, data: ChatInput, request: Request, agent_service: AgentService
    ) -> dict:
        """
        基本对话接口（非sse），用于和agent交互
        """
        try:
            client_info = {
                "client_ip": request.client[0] if request.client else None
            }
            result = await agent_service.chat_with_agent(
                user_id=data.user_id,
                input_text=data.input,
                client_info=client_info
            )
            return result
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    @post("/chat/stream")
    async def chat_with_agent_stream(self, data: ChatInput, agent_service: AgentService) -> ServerSentEvent:
        """
        流式对话接口（SSE），用于和agent交互
        """
        async def event_generator():
            try:
                for chunk in agent_service.chat_with_agent_stream(
                    user_id=data.user_id,
                    input_text=data.input
                ):
                    if hasattr(chunk, 'content'):
                        yield {"data": json.dumps({"response": chunk.content})}
                    else:
                        yield {"data": json.dumps({"response": str(chunk)})}
            except Exception as e:
                traceback.print_exc()
                yield {"data": json.dumps({"error": str(e)})}

        return ServerSentEvent(event_generator())

    @get("/todos/{user_id:str}")
    async def get_todos(self, user_id: str, agent_service: AgentService) -> dict:
        """
        返回用户id的所有 to do事项
        :param agent_service:
        :param user_id: 用户ID
        :return: 包含待办事项的字典
        """
        # 参数校验
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        try:
            # 调用服务层处理业务逻辑
            result = await agent_service.get_user_todos(user_id=user_id)
            return result
            
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    @get("/profile/{user_id:str}")
    async def get_profile(self, user_id: str, agent_service: AgentService) -> dict:
        """
        获取用户档案信息
        :param agent_service:
        :param user_id: 用户ID
        :return: 包含用户档案的字典
        """
        # 参数校验
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        try:
            # 调用服务层处理业务逻辑
            result = await agent_service.get_user_profile(user_id=user_id)
            return result
            
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    @get("/instructions/{user_id:str}")
    async def get_instructions(self, user_id: str, agent_service: AgentService) -> dict:
        """
        获取用户偏好说明
        :param agent_service:
        :param user_id: 用户ID
        :return: 包含用户偏好说明的字典
        """
        # 参数校验
        if not user_id or not user_id.strip():
            return {"error": "user_id不能为空"}
        
        try:
            # 调用服务层处理业务逻辑
            result = await agent_service.get_user_instructions(user_id=user_id)
            return result
            
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}