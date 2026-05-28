import os
import sys
import langchain
import openai
from openai import OpenAI
print('Hello, World!')
print(langchain.__version__)
print(openai.__version__)
import os
from openai import OpenAI

client = OpenAI(
    api_key="sk-24e556ae0b7d4598bb4dd88f6fb0dd46",   # 推荐通过环境变量配置，也可直接写死（不推荐）
    base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-v4-pro",  # 模型名称，必填项
    messages=[
        {"role": "system", "content": "你是一个有用的ai助手，协助用户解答问题。"},
        {"role": "user", "content":"你好啊，你可以帮我做什么？"},
    ],
    stream=False    # stream=False 非流式（一次性返回）、stream=True 流式（实时返回）
)



print(response.choices[0].message.content)

print("                                            ")
print("                                            ")
print("                                            ")

print(response)# print(response.choices[1].message.content)