from litestar import Litestar, get
from backend.controller.BasicAgentController import AgentChatController
from backend.utils.pg_pool import on_startup_pg_pool


@get("/")
async def index() -> str:
    return "Hello, world!"

app = Litestar(
    route_handlers=[
        index,
        AgentChatController,
    ],
    on_app_init=[on_startup_pg_pool]

)
