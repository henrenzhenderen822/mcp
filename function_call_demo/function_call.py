from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from weather_func import get_weather


load_dotenv()  # 载入 .env 文件中的环境变量
'''deepseek'''
# API_KEY = os.getenv("DEEPSEEK_API_KEY")
# BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
# MODEL = os.getenv("DEEPSEEK_MODEL_CHAT")
'''阿里大模型'''
API_KEY = os.getenv("ALI_API_KEY")
BASE_URL = os.getenv("ALI_BASE_URL")
MODEL = os.getenv("ALI_MODEL_QWEN")

# 初始化对话上下文
conversation_history = []  # 存储所有用户和 AI 的对话内容
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取一个地点的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "位置地点",
                    }
                },
                "required": ["location"]
            },
        }
    },
]


def llm_call(**kwargs):
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    response = client.chat.completions.create(
        model=MODEL,
        messages=kwargs.get("messages"),
        stream=kwargs.get("stream"),
        tools=kwargs.get("tools")
    )

    return response


def chat_loop():
    """运行交互式对话循环，维护上下文"""
    print("\n🚀 对话助手启动成功！")
    print("请输入你的问题，输入 'q' 可结束对话。\n")

    while True:
        user_input = input("👤 你: ").strip()

        if user_input.lower() == "q":
            print("🛑 结束对话，再见！")
            break

        # 记录用户输入到对话历史
        conversation_history.append({"role": "user", "content": user_input})
        # 发送请求
        response = llm_call(messages=conversation_history, tools=tools)

        if response:
            message = response.choices[0].message
            # print(message)
            # 工具字段
            tool = message.tool_calls
            if tool is not None:
                conversation_history.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tool[0].id,
                            "type": "function",
                            "function": {
                                "name": tool[0].function.name,
                                "arguments": tool[0].function.arguments,
                            }
                        }
                    ]
                })
                print("-"*50)
                print("工具调用：", tool)
                print("-"*50)
                weather_content = ""
                location = json.loads(tool[0].function.arguments)["location"]
                if tool[0].function.name == "get_weather":
                    weather_content = get_weather(location)                   # 调用函数 get_weather !
                conversation_history.append({"role": "tool", "tool_call_id": tool[0].id, "content": weather_content})
                # print(conversation_history)
                print("*"*50)
                for c in conversation_history:
                    print(c)
                print("*"*50)
                response_agin = llm_call(messages=conversation_history, tools=tools)
                print("🤖 AI:", response_agin.choices[0].message.content)
            else:
                print("*" * 50)
                for c in conversation_history:
                    print(c)
                print("*" * 50)
                print("🤖 AI:", message.content)
                conversation_history.append({"role": "assistant", "content": message.content})

            # print(ai_response)

            # 记录 AI 回复到对话历史
            print("\n")  # 换行
        else:
            print("⚠️ AI 响应失败，请稍后再试。")


# 启动聊天
if __name__ == "__main__":

    chat_loop()
