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
)

profile_extractor = create_extractor(
    model,
    tools=[Profile],
    tool_choice="Profile",
)

class UpdateMemory(TypedDict):
    """ Decision on what memory type to update """
    update_type: Literal['user', 'todo', 'instructions']


def task_mAIstro(state: CustomState, config: RunnableConfig, store: BaseStore):
    """从store中读取记忆，个性化chatbot的回应"""
    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Retrieve profile memory from the store
    namespace = ("profile", user_id)
    memories = store.search(namespace)
    if memories:
        user_profile = memories[0].value
    else:
        user_profile = None

    # Retrieve task memory from the store
    namespace = ("todo", user_id)
    memories = store.search(namespace)
    todo = "\n".join(f"{mem.value}" for mem in memories)

    # Retrieve custom instructions
    namespace = ("instructions", user_id)
    memories = store.search(namespace)
    instructions = "\n".join(f"{mem.value}" for mem in memories)

    system_msg = MODEL_SYSTEM_MESSAGE.format(user_profile=user_profile, todo=todo, instructions=instructions)

    # Respond using memory as well as the chat history
    response = model.bind_tools([UpdateMemory], parallel_tool_calls=False).invoke(
            [SystemMessage(content=system_msg)] + state["messages"]
    )
    return {"messages": [response]}


def update_profile(state: CustomState, config: RunnableConfig, store: BaseStore):
    """反映历史聊天，更新记忆集合"""
    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Define the namespace for the memories
    namespace = ("profile", user_id)

    # Retrieve the most recent memories for context
    existing_items = store.search(namespace)

    # Format the existing memories for the Trustcall extractor
    tool_name = "Profile"
    existing_memories = ([(existing_item.key, tool_name, existing_item.value)
                          for existing_item in existing_items]
                         if existing_items
                         else None
                         )

    # Merge the chat history and the instruction
    TRUSTCALL_INSTRUCTION_FORMATTED = TRUSTCALL_INSTRUCTION.format(time=datetime.now().isoformat())
    updated_messages = list(
        merge_message_runs(messages=[SystemMessage(content=TRUSTCALL_INSTRUCTION_FORMATTED)] + state["messages"][:-1]))

    # Invoke the extractor
    result = profile_extractor.invoke({"messages": updated_messages,
                                       "existing": existing_memories})

    # Save the memories from Trustcall to the store
    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(namespace,
                  rmeta.get("json_doc_id", str(uuid.uuid4())),
                  r.model_dump(mode="json"),
                  )
    tool_calls = state['messages'][-1].tool_calls
    return {"messages": [{"role": "tool", "content": "updated profile", "tool_call_id": tool_calls[0]['id']}]}


def update_todos(state: CustomState, config: RunnableConfig, store: BaseStore):
    """Reflect on the chat history and update the memory collection."""

    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    # Define the namespace for the memories
    namespace = ("todo", user_id)

    # Retrieve the most recent memories for context
    existing_items = store.search(namespace)

    # Format the existing memories for the Trustcall extractor
    tool_name = "ToDo"
    existing_memories = ([(existing_item.key, tool_name, existing_item.value)
                          for existing_item in existing_items]
                         if existing_items
                         else None
                         )

    # Merge the chat history and the instruction
    TRUSTCALL_INSTRUCTION_FORMATTED = TRUSTCALL_INSTRUCTION.format(time=datetime.now().isoformat())
    updated_messages = list(
        merge_message_runs(messages=[SystemMessage(content=TRUSTCALL_INSTRUCTION_FORMATTED)] + state["messages"][:-1]))

    # Initialize the spy for visibility into the tool calls made by Trustcall
    spy = Spy()

    # Create the Trustcall extractor for updating the ToDo list
    todo_extractor = create_extractor(
        model,
        tools=[ToDo],
        tool_choice=tool_name,
        enable_inserts=True
    ).with_listeners(on_end=spy)

    # Invoke the extractor
    result = todo_extractor.invoke({"messages": updated_messages,
                                    "existing": existing_memories})

    # Save the memories from Trustcall to the store
    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(namespace,
                  rmeta.get("json_doc_id", str(uuid.uuid4())),
                  r.model_dump(mode="json"),
                  )

    # Respond to the tool call made in task_mAIstro, confirming the update
    tool_calls = state['messages'][-1].tool_calls

    # Extract the changes made by Trustcall and add the the ToolMessage returned to task_mAIstro
    todo_update_msg = extract_tool_info(spy.called_tools, tool_name)
    return {"messages": [{"role": "tool", "content": todo_update_msg, "tool_call_id": tool_calls[0]['id']}]}


def update_instructions(state: CustomState, config: RunnableConfig, store: BaseStore):
    user_id = config["configurable"]["user_id"]
    namespace = ("instructions", user_id)

    existing_items = store.search(namespace)
    existing_instructions = [item.value.get("content") for item in existing_items] if existing_items else []

    current_text = "\n".join(existing_instructions)
    system_msg = CREATE_INSTRUCTIONS.format(current_instructions=current_text)
    new_memory = model.invoke(
        [SystemMessage(content=system_msg)] + state['messages'][:-1] + [
            HumanMessage(content="Please update the instructions based on the conversation, only return the instructions that need update")]
    )

    new_key = str(uuid.uuid4())
    store.put(namespace, new_key, Instruction(language="zh-CN", content=new_memory.content, key=new_key).model_dump())

    tool_calls = state['messages'][-1].tool_calls
    return {"messages": [{"role": "tool", "content": "appended instructions", "tool_call_id": tool_calls[0]['id']}]}


def route_message(state: CustomState, config: RunnableConfig, store: BaseStore) -> tuple[str, CustomState]:
    messages = state['messages']
    last_msg = messages[-1]

    # 没有 tool call，就结束
    if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
        return END, state

    # 构造 tool 响应
    tool_call = last_msg.tool_calls[0]
    update_type = tool_call["args"].get("update_type")

    tool_response = ToolMessage(
        tool_call_id=tool_call["id"],
        content="acknowledged"
    )

    new_state: CustomState = {
        **state,
        "messages": messages + [tool_response]
    }

    if update_type == "user":
        return "update_profile", new_state
    elif update_type == "todo":
        return "update_todos", new_state
    elif update_type == "instructions":
        return "update_instructions", new_state
    else:
        raise ValueError(f"[route_message] 无效的 update_type: {update_type}")

