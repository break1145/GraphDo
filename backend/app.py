from litestar import Litestar, get
from backend.controller.AgentChatController import AgentChatController


@get("/")
async def index() -> str:
    return "Hello, world!"

app = Litestar(
    route_handlers=[
        index,
        AgentChatController,
    ]
)
