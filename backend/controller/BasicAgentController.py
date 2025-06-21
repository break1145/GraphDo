from litestar import Litestar, get, post, Controller
from pydantic import BaseModel
from litestar.connection import Request
from backend.agent.core import ToDoAgent
import traceback

agent = ToDoAgent()

class ChatInput(BaseModel):
    user_id: str
    input: str


class AgentChatController(Controller):
    path = "/agent"

    @post("/chat")
    async def chat_with_agent(self, data: ChatInput, request: Request) -> dict:
        """
        基本对话接口（非sse），用于和agent交互
        :param data: 输入参数
        :param request: 默认请求
        :return: 包含response的字典
        """
        try:
            print(f"Request method: {request.method}")
            print(f"Client address: {request.client}")

            response = agent.chat(user_id=data.user_id, input=data.input, stream=False)
            return {
                "response": response.content,
                "client_ip": request.client[0]
            }
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    @get("/todos/{user_id:str}")
    async def get_todos(self, user_id: str) -> dict:
        """
        返回用户id的所有 to do事项
        :param user_id:
        :return:
        """
        try:
            todos = agent.get_todos(user_id=user_id)
            return {"response": todos}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    @get("/profile/{user_id:str}")
    async def get_profile(self, user_id: str) -> dict:
        """
        获取用户档案信息
        :param user_id: 用户ID
        :return: 包含用户档案的字典
        """
        try:
            profile = agent.get_profile(user_id=user_id)
            return {"response": profile}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    @get("/instructions/{user_id:str}")
    async def get_instructions(self, user_id: str) -> dict:
        """
        获取用户偏好说明
        :param user_id: 用户ID
        :return: 包含用户偏好说明的字典
        """
        try:
            instructions = agent.get_instructions(user_id=user_id)
            return {"response": instructions}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}