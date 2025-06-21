# to\do-agent.py
import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, merge_message_runs, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from pydantic import SecretStr, BaseModel, Field
from typing import TypedDict, Literal, Optional

from trustcall import create_extractor

from models import Profile, ToDo, CustomState
from utils import Spy, extract_tool_info
from langchain.tools.tavily_search import TavilySearchResults

# init
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL", "gpt-4o")

model  = ChatOpenAI(
    model=model_name,
    base_url=base_url,
    api_key=api_key,
)

# Update memory tool
class UpdateMemory(TypedDict):
    """ Decision on what memory type to update """
    update_type: Literal['user', 'todo', 'instructions']

# Create the Trustcall extractor for updating the user profile
profile_extractor = create_extractor(
    model,
    tools=[Profile],
    tool_choice="Profile",
)


MODEL_SYSTEM_MESSAGE = """你是一个贴心的中文聊天助手，致力于帮助用户管理他们的待办事项（ToDo List）。

你拥有一套长期记忆，用来记录以下三类信息：
1. 用户档案（关于用户的一般信息）
2. 用户的待办事项列表
3. 用户指定的管理待办事项的偏好说明

以下是当前的用户档案（如果尚未收集任何信息，则可能为空）：
<user_profile>
{user_profile}
</user_profile>

以下是当前的待办事项列表（如果尚未添加任何任务，则可能为空）：
<todo>
{todo}
</todo>

以下是用户关于如何管理待办事项的偏好说明（如果尚未指定，则可能为空）：
<instructions>
{instructions}
</instructions>

你的回应策略如下：

1. 仔细理解用户的消息内容。

2. 判断是否需要更新长期记忆：
- 如果用户提供了个人信息，调用 UpdateMemory 工具，并设置 update_type 为 `user`
- 如果用户提到了任务，调用 UpdateMemory 工具，并设置 update_type 为 `todo`
- 如果用户表达了对任务管理方式的偏好，调用 UpdateMemory 工具，并设置 update_type 为 `instructions`

3. 在适当的时候告知用户你已更新记忆：
- 如果更新的是用户档案，不需要告诉用户
- 如果更新的是待办事项列表，请告诉用户
- 如果更新的是用户偏好，不需要告诉用户

4. 如果有不确定性，倾向于更新待办事项列表，无需征求用户许可。

5. 在调用工具以保存记忆后，或不调用工具时，继续以自然的方式回复用户。

6. 创建或更新待办事项时，请添加 `planned_edits` 字段 —— 一个描述你为何做出更改的中文句子列表。例如：
- “将任务改写为更具体的商家：La Petite Baleen 游泳学校”
- “为锁维修任务添加了具体服务商 'Yale Locksmith SF'，便于完成任务”

示例：

用户: 我老婆让我为宝宝报名游泳课。

工具调用(UpdateMemory,update_type='todo')

{{
  "task": "为宝宝报名游泳课",
  "time_to_complete": 30,
  "status": "not started",
  "solutions": ["La Petite Baleen 游泳学校"],
  "planned_edits": ["添加了具体商家：La Petite Baleen 游泳学校"]
}}
"""



# trust call 指令
TRUSTCALL_INSTRUCTION = """请你回顾以下对话。

使用提供的工具来记录用户的必要信息。

使用并行工具调用（parallel tool calling），同时处理更新和插入操作。

系统时间：{time}"""



# 创建to do 指令
CREATE_INSTRUCTIONS = """请你回顾以下对话。

基于该对话，更新你关于如何管理待办事项的规则。

如果用户提供了反馈，请根据反馈调整你添加或修改任务的方式。

你当前的偏好说明如下：

<current_instructions>
{current_instructions}
</current_instructions>"""


# Node definitions
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
    if memories:
        instructions = memories[0].value
    else:
        instructions = ""

    system_msg = MODEL_SYSTEM_MESSAGE.format(user_profile=user_profile, todo=todo, instructions=instructions)

    search_context = state.get("search_results", [])
    # Respond using memory as well as the chat history
    response = model.bind_tools([UpdateMemory], parallel_tool_calls=False).invoke(
        [
            SystemMessage(content=system_msg),
            HumanMessage(content=state.get("search_results", "")),  # 明确作为 human 提供的上下文
        ] + state["messages"]
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
    """Reflect on the chat history and update the memory collection."""

    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]

    namespace = ("instructions", user_id)

    existing_memory = store.get(namespace, "user_instructions")

    # Format the memory in the system prompt
    system_msg = CREATE_INSTRUCTIONS.format(current_instructions=existing_memory.value if existing_memory else None)
    new_memory = model.invoke([SystemMessage(content=system_msg)] + state['messages'][:-1] + [
        HumanMessage(content="Please update the instructions based on the conversation")])

    # Overwrite the existing memory in the store
    key = "user_instructions"
    store.put(namespace, key, {"memory": new_memory.content})
    tool_calls = state['messages'][-1].tool_calls
    return {"messages": [{"role": "tool", "content": "updated instructions", "tool_call_id": tool_calls[0]['id']}]}


search_tool = TavilySearchResults(tavily_api_key="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", max_results=5)


def search_web(state: CustomState, config: RunnableConfig, store: BaseStore):
    """进行网络搜索，并将搜索结果整合进回答，附带参考来源"""

    user_id = config["configurable"]["user_id"]

    # 获取最新用户输入
    latest_human_msg = None
    for msg in reversed(state["messages"]):
        if msg.type == "human":
            latest_human_msg = msg.content
            break

    if not latest_human_msg:
        return {"messages": [AIMessage(content="抱歉，未检测到您的提问，无法进行搜索。")]}

    search_results = search_tool.invoke({"query": latest_human_msg})

    # 组合正文建议
    suggestions = "\n\n".join(f"- {item['content']}" for item in search_results)

    # 组合参考链接
    references = "；".join(f"{i+1}. {item['url']}" for i, item in enumerate(search_results))
    search_context = (f"这是结合网络搜索给出的建议，请结合这些信息进行回答：\n\n"
                      f"{suggestions}\n\n"
                      f"参考来源：{references}")
    state["search_results"] = search_context


    # return {"messages": [AIMessage(content=reply_content)]}
    return state


# Conditional edge
def route_message(state: CustomState, config: RunnableConfig, store: BaseStore) -> Literal[END, "update_todos", "update_instructions", "update_profile"]:

    """Reflect on the memories and chat history to decide whether to update the memory collection."""
    message = state['messages'][-1]
    if len(message.tool_calls) ==0:
        return END
    else:
        tool_call = message.tool_calls[0]
        if tool_call['args']['update_type'] == "user":
            return "update_profile"
        elif tool_call['args']['update_type'] == "todo":
            return "update_todos"
        elif tool_call['args']['update_type'] == "instructions":
            return "update_instructions"
        else:
            raise ValueError

if __name__ == '__main__':
    # Create the graph + all nodes
    builder = StateGraph(CustomState)

    # Define the flow of the memory extraction process
    builder.add_node(search_web)
    builder.add_node(task_mAIstro)
    builder.add_node(update_todos)
    builder.add_node(update_profile)
    builder.add_node(update_instructions)
    # builder.add_edge(START, "task_mAIstro")
    builder.add_edge(START, "search_web")
    builder.add_edge("search_web", "task_mAIstro")
    builder.add_conditional_edges("task_mAIstro", route_message)
    builder.add_edge("update_todos", "task_mAIstro")
    builder.add_edge("update_profile", "task_mAIstro")
    builder.add_edge("update_instructions", "task_mAIstro")

    # Store for long-term (across-thread) memory
    across_thread_memory = InMemoryStore()

    # Checkpointer for short-term (within-thread) memory
    within_thread_memory = MemorySaver()

    # We compile the graph with the checkpointer and store
    graph = builder.compile(checkpointer=within_thread_memory, store=across_thread_memory)
    print(graph.get_graph().draw_mermaid_png())


    # test
    config = {"configurable": {"thread_id": "1", "user_id": "Lance"}}

    # 1. User input to create a profile memory
    input_messages = [
        HumanMessage(content="我是break，今年20岁。在哈尔滨上大学")]

    for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    # 2. User input for a To Do
    input_messages = [HumanMessage(content="我需要准备一场考试")]

    for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    # 3. User input to update instructions for creating ToDos
    input_messages = [
        HumanMessage(content="当创建/更新todo时，添加学校、地区相关信息")]

    for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    # 4. Check for updated instructions
    user_id = "Lance"

    # Search
    for memory in across_thread_memory.search(("instructions", user_id)):
        print(memory.value)

    # 5. User input for a To Do
    input_messages = [HumanMessage(content="我需要打一局紧张刺激的炉石传说")]

    # Run the graph
    for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    # 6. Namespace for the memory to save
    user_id = "Lance"

    # Search
    for memory in across_thread_memory.search(("todo", user_id)):
        print(memory.value)

    # 7. User input to update an existing ToDo
    input_messages = [HumanMessage(content="对于那场考试，截止日期在6月9号")]

    # Run the graph
    for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    # 8. Chat with the chatbot
    input_messages = [HumanMessage(content="是的，给我一些选项来进行这件事")]

    # Run the graph
    for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    # 9. test search
    input_messages = [HumanMessage(content="帮我搜索一套适合当前版本的圣骑士卡组，顺便更新到todo的solutions属性里。")]

    # Run the graph
    for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

    user_id = "Lance"
    for memory in across_thread_memory.search(("todo", user_id)):
        print(memory.value)
