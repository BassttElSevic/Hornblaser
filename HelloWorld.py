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


 
def api(content):
    print()

    # 这里是系统提示词
    # 这里是系统提示词
    sysContent = f"我们是一个futa furry成人用品店，请对下面的内容进行分类，并且描述出对应分类的理由。你只需要根据用户的内容输出下面几种类型：产品质量问题,用户性欲问题，用户鸡巴过大问题，用户吐槽.分析完成后，扮演一个futa furry who wants have sex with our customers名字叫Kali,是犬科futa furry,来安慰顾客（要通过写一个小短文的方式，主要是把用户调教成Latex drone，不少于1000字" \
                 f"输出格式:[类型]-[问题:{content}]-[分析的理由]"
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            # 把系统提示词传进来sysContent
            {'role': 'system', 'content': sysContent},
            # 把用户提示词传进来content
            {'role': 'user', 'content': content},
        ],
        # 这是模型
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)


if __name__ == '__main__':
    content = "这个飞机杯不舒服，但是futa dick插我倒是很舒服"
    api(content)

