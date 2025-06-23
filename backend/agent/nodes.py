import json
import uuid
from datetime import datetime
from langchain_core.messages import SystemMessage, merge_message_runs, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from typing import Literal, TypedDict
from langgraph.constants import END
from trustcall import create_extractor
from .models import Profile, ToDo, CustomState, Instruction
from .utils import Spy, extract_tool_info
from .constants import MODEL_SYSTEM_MESSAGE, TRUSTCALL_INSTRUCTION, CREATE_INSTRUCTIONS
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langchain_core.messages import ToolMessage


load_dotenv()

model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
).with_config({
    "system_message": "你是一个中文助手，请始终用简体中文回答。",
})

profile_extractor = create_extractor(
    model,
    tools=[Profile],
    tool_choice="Profile",
)

class UpdateMemory(TypedDict):
    """ Decision on what memory type to update """
    update_type: Literal['user', 'todo', 'instructions']


def task_mAIstro(state: CustomState, config: RunnableConfig, store: BaseStore):
    """从 store 中读取记忆，个性化 chatbot 的回应，并处理工具调用后的回复"""

    # Get user ID
    user_id = config["configurable"]["user_id"]

    # Step 1: 获取用户长期记忆：Profile / To Do / Instructions
    namespace_profile = ("profile", user_id)
    profile_memories = store.search(namespace_profile)
    user_profile = profile_memories[0].value if profile_memories else None

    namespace_todo = ("todo", user_id)
    todo_memories = store.search(namespace_todo)
    todo = "\n".join(json.dumps(mem.value, ensure_ascii=False) for mem in todo_memories)

    namespace_instructions = ("instructions", user_id)
    instructions_memories = store.search(namespace_instructions)
    instructions = "\n".join(json.dumps(mem.value) for mem in instructions_memories)

    # Step 2: 生成系统提示词
    system_msg = MODEL_SYSTEM_MESSAGE.format(
        user_profile=user_profile,
        todo=todo,
        instructions=instructions
    )

    # Step 3: 构造初始消息
    system_messages = [
        SystemMessage(content="你是一个中文助手，请始终用简体中文回答。"),
        SystemMessage(content=system_msg)
    ]
    messages = system_messages + state["messages"]

    # Step 4: 如果上一条是 ToolMessage，说明上轮刚执行了工具，继续补全自然语言响应
    if isinstance(state["messages"][-1], ToolMessage):
        # 继续调用模型让其根据工具调用结果生成自然语言回复
        response = model.invoke(messages)
        return {"messages": [response]}

    # Step 5: 否则正常执行对话逻辑（包括可能触发工具调用）
    response = model.bind_tools([UpdateMemory], parallel_tool_calls=False).invoke(messages)
    return {"messages": [response]}


def update_profile(state: CustomState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"]["user_id"]
    namespace = ("profile", user_id)
    existing_items = store.search(namespace)

    tool_name = "Profile"
    existing_memories = ([(item.key, tool_name, item.value) for item in existing_items] if existing_items else None)

    TRUSTCALL_INSTRUCTION_FORMATTED = TRUSTCALL_INSTRUCTION.format(time=datetime.now().isoformat())
    updated_messages = list(merge_message_runs(
        messages=[SystemMessage(content=TRUSTCALL_INSTRUCTION_FORMATTED)] + state["messages"][:-1]
    ))

    result = profile_extractor.invoke({
        "messages": updated_messages,
        "existing": existing_memories
    })

    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(namespace, rmeta.get("json_doc_id", str(uuid.uuid4())), r.model_dump(mode="json"))

    tool_calls = state['messages'][-1].tool_calls
    return {
        "messages": [
            ToolMessage(tool_call_id=call['id'], content="done") for call in tool_calls
        ]
    }

def update_todos(state: CustomState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"]["user_id"]
    namespace = ("todo", user_id)
    existing_items = store.search(namespace)

    tool_name = "ToDo"
    existing_memories = ([(item.key, tool_name, item.value) for item in existing_items] if existing_items else None)

    TRUSTCALL_INSTRUCTION_FORMATTED = TRUSTCALL_INSTRUCTION.format(time=datetime.now().isoformat())
    updated_messages = list(merge_message_runs(
        messages=[SystemMessage(content=TRUSTCALL_INSTRUCTION_FORMATTED)] + state["messages"][:-1]
    ))

    spy = Spy()

    todo_extractor = create_extractor(
        model,
        tools=[ToDo],
        tool_choice=tool_name,
        enable_inserts=True
    ).with_listeners(on_end=spy)

    result = todo_extractor.invoke({
        "messages": updated_messages,
        "existing": existing_memories
    })

    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(namespace, rmeta.get("json_doc_id", str(uuid.uuid4())), r.model_dump(mode="json"))

    tool_calls = state['messages'][-1].tool_calls

    print("[工具调用] ToDo 更新：", extract_tool_info(spy.called_tools, tool_name))

    return {
        "messages": [
            ToolMessage(tool_call_id=call['id'], content="done") for call in tool_calls
        ]
    }


def update_instructions(state: CustomState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"]["user_id"]
    namespace = ("instructions", user_id)
    existing_items = store.search(namespace)
    existing_instructions = [item.value.get("content") for item in existing_items] if existing_items else []

    current_text = "\n".join(existing_instructions)
    system_msg = CREATE_INSTRUCTIONS.format(current_instructions=current_text)

    new_memory = model.invoke(
        [SystemMessage(content=system_msg)] + state['messages'][:-1] + [
            HumanMessage(content="请根据对话更新 instructions（用户偏好），只需要返回新增的部分。")]
    )

    new_key = str(uuid.uuid4())
    store.put(namespace, new_key, Instruction(
        language="zh-CN",
        content=new_memory.content,
        key=new_key
    ).model_dump())

    tool_calls = state['messages'][-1].tool_calls
    return {
        "messages": [
            ToolMessage(tool_call_id=call['id'], content="done") for call in tool_calls
        ]
    }

def route_message(state: CustomState, config: RunnableConfig, store: BaseStore) -> tuple[str, CustomState]:
    messages = state['messages']
    last_msg = messages[-1]

    # 没有 tool call，就结束
    if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
        return END, state

    new_messages = messages[:]
    update_types = []

    for tool_call in last_msg.tool_calls:
        update_type = tool_call["args"].get("update_type")
        update_types.append(update_type)

        # 加入 tool 响应
        tool_response = ToolMessage(
            tool_call_id=tool_call["id"],
            content="acknowledged"
        )
        new_messages.append(tool_response)

    new_state: CustomState = {
        **state,
        "messages": new_messages
    }

    # 逐个分支跳转执行工具更新
    # 用 langgraph 的“多分支支持”处理（你应该在 flow 中对每个 update_type 建立分支）
    if "user" in update_types:
        return "update_profile", new_state
    elif "todo" in update_types:
        return "update_todos", new_state
    elif "instructions" in update_types:
        return "update_instructions", new_state
    else:
        raise ValueError(f"[route_message] 无效的 update_type: {update_types}")

