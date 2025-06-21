# core.py
import uuid
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.store.memory import InMemoryStore
from langgraph.graph import StateGraph

from .models import CustomState
from .nodes import (
    task_mAIstro, update_profile, update_todos, update_instructions,
    route_message,
)


class ToDoAgent:
    def __init__(self):
        # 初始化 memory
        self.across_thread_memory = InMemoryStore()
        self.within_thread_memory = MemorySaver()

        # 构建 graph
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(CustomState)

        builder.add_node(task_mAIstro)
        builder.add_node(update_todos)
        builder.add_node(update_profile)
        builder.add_node(update_instructions)

        builder.add_edge(START, "task_mAIstro")
        builder.add_conditional_edges("task_mAIstro", route_message)
        builder.add_edge("update_todos", "task_mAIstro")
        builder.add_edge("update_profile", "task_mAIstro")
        builder.add_edge("update_instructions", "task_mAIstro")

        return builder.compile(
            checkpointer=self.within_thread_memory,
            store=self.across_thread_memory
        )

    def chat(
            self,
            user_id: str,
            input: str | List[BaseMessage],
            thread_id: str = None,
            stream: bool = False,
    ):
        """对话方法：传入消息并获取响应"""
        try:
            print(f"[Chat] user_id={user_id}, input={input}")

            if isinstance(input, str):
                input_messages = [HumanMessage(content=input)]
            else:
                input_messages = input

            config = {
                "configurable": {
                    "thread_id": thread_id or str(uuid.uuid4()),
                    "user_id": user_id,
                }
            }

            input_state = {"messages": input_messages}

            if stream:
                return self._chat_stream(input_state, config)
            else:
                result = None
                for chunk in self.graph.stream(input_state, config, stream_mode="values"):
                    print("[Chat Chunk]", chunk)
                    result = chunk["messages"][-1]

                # 加上类型检查
                if result is None:
                    raise ValueError("chat() 最终返回的 result 为 None，可能 graph 未正确执行")
                if not hasattr(result, "content"):
                    raise TypeError(f"返回值类型错误：{type(result)}，缺少 .content 属性")

                print(f"[Chat] Final response content: {result.content}")
                return result

        except Exception as e:
            import traceback
            print("[Chat] Exception caught in chat()")
            traceback.print_exc()
            raise e

    def _chat_stream(self, input_state, config):
        """流式聊天的内部方法"""
        for chunk in self.graph.stream(input_state, config, stream_mode="values"):
            print("[Chat Stream Chunk]", chunk)
            yield chunk["messages"][-1]

    def get_todos(self, user_id: str):
        """查看 to do 列表"""
        return [item.value for item in self.across_thread_memory.search(("todo", user_id))]

    def get_profile(self, user_id: str):
        """查看用户档案"""
        memories = self.across_thread_memory.search(("profile", user_id))
        return memories[0].value if memories else None

    def get_instructions(self, user_id: str):
        """查看偏好说明"""
        memories = self.across_thread_memory.search(("instructions", user_id))
        return memories[0].value if memories else None
