import os
import sys
import langchain
import openai
from openai import OpenAI
print('Hello, World!')
print(langchain.__version__)
print(openai.__version__)

api_key = os.getenv("DEEP_SEEK_API")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com")


# 关键：设置 stream=True
response = client.chat.completions.create(
    model="deepseek-v4-pro",      # 用的模型名，换了就能切别的模型（必填）
    messages=[                    # 对话内容，一个列表，装着每条消息
        {"role": "system", "content": "你是一个有用的助手"},
        #       ↑ 系统提示               ↑ 设定AI的人设/行为规则
        {"role": "user", "content": "你好啊，你能为我做什么"},
        #       ↑ 用户发言               ↑ 你实际想问的问题
    ],
    stream=False  # False=等AI写完一次性返回（简单省事）
)    

# 逐块获取生成内容
print(response.choices[0].message.content)