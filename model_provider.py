import os, json
import dashscope
from prompt import user_prompt
from dashscope.api_entities.dashscope_response import Message

class ModelProvider(object):
    def __init__(self):
        # 从环境变量中获取API密钥和模型名称
        self.api_key = os.environ.get('DASH_SCOPE_API_KEY')
        self.model_name = os.environ.get('MODEL_NAME')
        # 初始化dashscope客户端
        self._client = dashscope.Generation()
        # 设置最大重试次数
        self.max_retry_time = 1

    def chat(self, prompt, chat_history):
        cur_retry_time = 0
        while cur_retry_time < self.max_retry_time:
            cur_retry_time += 1
            try:
                # 构建消息列表，包括系统提示、用户提示和历史聊天记录
                messages = [
                    Message(role="system", content=prompt),
                    Message(role="user", content=user_prompt)
                ]
                for his in chat_history:
                    messages.append(Message(role="user", content=his[0]))
                    messages.append(Message(role="assistant", content=his[1]))
                # 调用模型API并获取响应
                response = self._client.call(
                    model=self.model_name,
                    api_key=self.api_key,
                    messages=messages
                )

                print(response)
                # 解析模型响应并返回内容
                content = self._parse_model_response(response)
                return content
            except Exception as e:
                print(f"call llm exception: {e}")
        return {}

    def _parse_model_response(self, response):
        """尝试解析模型响应为JSON格式"""
        text = response["output"]["text"]
        try:
            # 尝试直接解析文本为JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试查找被标记的JSON字符串
            json_start = text.find("```json")
            json_end = text.rfind("```")
            json_content = text[json_start + 7:json_end]
            return json.loads(json_content)
