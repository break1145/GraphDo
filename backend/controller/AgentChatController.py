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

    @get("/chat/test/{user_id:str}")
    async def chat_with_agent(self, user_id: str) -> dict:
        try:
            response = agent.chat(user_id=user_id, input="我需要准备考试", stream=False)
            print("[Route] Response from agent.chat:", response)

            return {"response": response.content}
        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}

    @post("/chat")
    async def chat_with_agent(self, data: ChatInput, request: Request) -> dict:
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