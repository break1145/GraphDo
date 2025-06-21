# core.py
import os
import uuid
from typing import List
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.store.postgres import PostgresStore
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from .models import CustomState
from .nodes import (
    task_mAIstro, update_profile, update_todos, update_instructions,
    route_message,
)


class ToDoAgent:
    def __init__(self):
        self.connection_pool = None
        self.across_thread_memory = None
        self.within_thread_memory = None
        self.graph = None

        self.setup()

    def setup(self):
        load_dotenv()
        db_uri = os.getenv("DB_URI")
        try:
            # 尝试建立pg连接池
            self.connection_pool = ConnectionPool(
                conninfo=db_uri,
                kwargs={
                    "row_factory": dict_row,
                    "autocommit": True
                }
            )

            self.across_thread_memory = PostgresStore(self.connection_pool)
            self.within_thread_memory = PostgresSaver(self.connection_pool)

            self.across_thread_memory.setup()
            self.within_thread_memory.setup()

            print("[ToDoAgent] PostgreSQL连接成功")

        except Exception as e:
            print(f"[ToDoAgent] PostgreSQL连接失败: {e}")
            print("[ToDoAgent] 回退到内存存储")
            from langgraph.checkpoint.memory import MemorySaver
            from langgraph.store.memory import InMemoryStore
            self.across_thread_memory = InMemoryStore()
            self.within_thread_memory = MemorySaver()

        self.graph = self._build_graph()
        print("[ToDoAgent] graph编译成功")

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
        """
        对话方法：传入消息并获取响应
        :param user_id: 用户id，与记忆关联
        :param input: 输入信息
        :param thread_id: 对话id
        :param stream: 是否流式返回
        :return: if stream: 返回流式生成器; else: 返回llm invoke的响应
        """

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

    def __del__(self):
        """清理连接池"""
        if hasattr(self, 'connection_pool'):
            try:
                self.connection_pool.close()
            except:
                pass
