from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore


def create_store_and_checkpoint():
    """
    初始化长短期内存：
    - InMemoryStore 用于长期存储（如 Profile/ToDo）
    - MemorySaver 用于线程级的短期上下文（对话历史）
    """
    store = InMemoryStore()
    checkpoint = MemorySaver()
    return store, checkpoint


# 可选：提供直接可用的全局 store 和 checkpoint
store, checkpoint = create_store_and_checkpoint()
