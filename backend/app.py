from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from backend.controller.BasicAgentController import AgentChatController
from backend.controller.CommonController import CommonController
from backend.utils.pg_pool import on_startup_pg_pool, close_pg_pool


@get("/")
async def index() -> str:
    return "Hello, world!"

# 配置 CORS
cors_config = CORSConfig(
    allow_origins=["http://localhost:5173"],  # 前端开发服务器地址
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)

app = Litestar(
    route_handlers=[
        index,
        AgentChatController,
        CommonController
    ],
    on_app_init=[on_startup_pg_pool],
    on_shutdown=[lambda: close_pg_pool()],
    cors_config=cors_config,
)
