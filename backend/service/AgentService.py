from litestar.di import Provide

from backend.agent.core import ToDoAgent


class AgentService:

    def __init__(self):
        self.agent = ToDoAgent()
    
    async def chat_with_agent(self, user_id: str, input_text: str, client_info: dict = None) -> dict:
        """
        处理与agent的对话业务逻辑
        :param user_id: 用户ID
        :param input_text: 输入文本
        :param client_info: 客户端信息（可选）
        :return: 包含响应内容的字典
        """
        response = self.agent.chat(user_id=user_id, input=input_text, stream=False)
        
        result = {
            "response": response.content
        }
        
        # 如果有客户端信息，添加到响应中
        if client_info:
            result.update(client_info)
            
        return result

    def chat_with_agent_stream(self, user_id: str, input_text: str):
        """
        处理与agent的流式对话业务逻辑
        :param user_id: 用户ID
        :param input_text: 输入文本
        :return: 流式响应生成器
        """
        return self.agent.chat(user_id=user_id, input=input_text, stream=True)
    
    # async def get_user_todos(self, user_id: str) -> dict:
    #     """
    #     获取用户的待办事项
    #     :param user_id: 用户ID
    #     :return: 包含待办事项列表的字典
    #     """
    #     todos = self.agent.get_todos(user_id=user_id)
    #     return {"response": todos}
    #
    # async def get_user_profile(self, user_id: str) -> dict:
    #     """
    #     获取用户档案信息
    #     :param user_id: 用户ID
    #     :return: 包含用户档案的字典
    #     """
    #     profile = self.agent.get_profile(user_id=user_id)
    #     return {"response": profile}
    #
    # async def get_user_instructions(self, user_id: str) -> dict:
    #     """
    #     获取用户偏好说明
    #     :param user_id: 用户ID
    #     :return: 包含用户偏好说明的字典
    #     """
    #     instructions = self.agent.get_instructions(user_id=user_id)
    #     return {"response": instructions}