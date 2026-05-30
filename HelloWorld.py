import os
from os import error
import sys
import langchain
import openai
import time
from openai import OpenAI
print('Hello, World!')
print(langchain.__version__)
print(openai.__version__)

api_key = os.getenv("DEEP_SEEK_API")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com")


def api(content):
    print()
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[
                {"role": "system","content": "你是一个ai助手，用来解决我们店里遇到的问题"},
                {"role": "user","content": content}
            ],
            stream=False
        )
        print(response.choices[0].message.content)
    except error:
        time.sleep(10)
        print("请求失败，正在重试...")


if __name__ == '__main__':
    content = "你们为啥发货的时候，没给我发螺丝？忘记了吗？"
    api(content)

