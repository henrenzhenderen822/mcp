# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

'''deepseek'''
# API_KEY = os.getenv("DEEPSEEK_API_KEY")
# BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
# MODEL = os.getenv("DEEPSEEK_MODEL_CHAT")
'''阿里大模型'''
API_KEY = os.getenv("ALI_API_KEY")
BASE_URL = os.getenv("ALI_BASE_URL")
MODEL = os.getenv("ALI_MODEL_QWEN")


def llm_call(**kwargs):
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    response = client.chat.completions.create(
        model=MODEL,
        messages=kwargs.get("messages"),
        # stream=True,
        tools=kwargs.get("tools")
    )

    return response


if __name__ == '__main__':
    query = "你好"

    messages = [{
        "role": "user",
        "content": query
    }]

    response = llm_call(messages=messages)
    print(response.choices[0].message.content)



