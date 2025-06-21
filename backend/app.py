from litestar import Litestar, get
from agent.core import ToDoAgent
from backend.controller.AgentChatController import AgentChatController

agent = ToDoAgent()

@get("/")
async def index() -> str:
    return "Hello, world!"


app = Litestar(route_handlers=[
    index,
    AgentChatController,

    ])
