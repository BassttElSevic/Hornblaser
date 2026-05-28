import os
import sys
import langchain
import openai
from openai import OpenAI
print('Hello, World!')
print(langchain.__version__)
print(openai.__version__)

client = OpenAI(
    api_key="sk-24e556ae0b7d4598bb4dd88f6fb0dd46",   # 推荐通过环境变量配置，也可直接写死（不推荐）
    base_url="https://api.deepseek.com")


# 关键：设置 stream=True
YAJU = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是日本的野兽先辈"},
        {"role": "user", "content": "兄啊，给我讲个关于homo的笑话吧（急不可耐"}
    ],
    stream=True   # 开启流式
)

# 逐块获取生成内容
for homo in YAJU:
    if homo.choices[0].delta.content: 
        print(homo.choices[0].delta.content, end="", flush=True)