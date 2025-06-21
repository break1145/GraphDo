from litestar import Litestar, get
from agent.core import ToDoAgent

agent = ToDoAgent()

@get("/")
async def index() -> str:
    return "Hello, world!"

@get("/books/{book_id:int}")
async def get_book(book_id: int) -> dict[str, int]:
    return {"book_id": book_id}

@get("/chat/{user_id:str}")
async def chat_with_agent(user_id: str) -> dict:
    try:
        response = agent.chat(user_id=user_id, input="我需要准备考试", stream=False)
        print("[Route] Response from agent.chat:", response)

        return {"response": response}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}



@get("/todos/{user_id:str}")
async def get_todos(user_id: str) -> dict:
    todos = agent.get_todos(user_id)
    return {"todos": todos}

app = Litestar([index, get_book, chat_with_agent, get_todos])
