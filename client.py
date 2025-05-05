import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys
# from anthropic import Anthropic    # 这里不使用Anthropic提供的模型，改为自己的模型接口
from llm_api import llm_call

from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # 初始化 - 会话、客户端、大模型
        self.session: Optional[ClientSession] = None      # MCP会话，初始化为空
        self.exit_stack = AsyncExitStack()                # 用于管理资源的异步上下文
        self.llm = llm_call                               # 自定义大模型接口

    async def connect_to_server(self, server_script_path: str):
        """
            连接到MCP服务器（python或者javascript）
            server_script_path: 服务器的脚本路径 (.py 或者 .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或者 .js 文件")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        # ************* 通过 stdio 连接到服务器 *************
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # 获取服务器支持的工具列表
        response = await self.session.list_tools()
        tools = response.tools
        print("\n成功连接MCP服务器，已加载工具:", [tool.name for tool in tools])

    async def process_query(self, messages: list) -> list:
        """
            处理用户输入查询，并通过 LLM 获取响应（支持工具调用）
            参数：用户输入的文本
            返回：处理后的响应文本
        """
        #
        response = await self.session.list_tools()
        # 官网使用大模型API自带的函数调用，这里同样借助函数调用，使用阿里qwen_plus模型的格式 https://bailian.console.aliyun.com/?tab=api#/api/?type=model&url=https%3A%2F%2Fhelp.aliyun.com%2Fdocument_detail%2F2712576.html
        # 如果模型不带functioncall功能需要使用提示词并从大模型回答中提取是否调用工具
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
        } for tool in response.tools]

        # print(available_tools)

        # 初始化 API 调用
        response = self.llm(
            messages=messages,
            tools=available_tools
        )

        # print(response)

        # 处理 LLM 响应，可能包含文本或工具调用
        tool_results = []   # 存储工具调用结果
        final_text = []     # 存储最终生成文本

        llm_tools = response.choices[0].message.tool_calls
        llm_content = response.choices[0].message.content
        # 如果触发了函数调用
        if llm_tools:
            if len(llm_tools) > 1:
                print("多工具调用！")
            for tool in llm_tools:
                # 从模型返回结果中获取调用的函数和对应参数
                tool_name = tool.function.name
                tool_args = json.loads(tool.function.arguments)
                print(f"调用工具:{tool_name},参数:{tool_args}")
                tool_id = tool.id
                # 通过 MCP 服务器调用工具
                result = await self.session.call_tool(tool_name, tool_args)  # ***** 通过MCP提供的"call_tool"方法调用工具 *****
                # print(result)
                res = ""
                for c in result.content:
                    res += c.text
                # 将工具结果加入消息列表，继续对话
                messages.append({
                    "role": "system",
                    "content": "调用工具返回结果：" + res
                })
                print("\n🚀工具返回结果：" + res)

                print(messages)

                # 再次调用 LLM，基于工具结果继续生成对话
                response = self.llm(messages=messages)

                print(response.choices[0].message.content)

                # final_text.append(response.choices[0].message.content)

        elif llm_content:
            print("\n🤖回复：" + llm_content)
            messages.append({
                "role": "assistant",
                "content": llm_content
            })

        else:
            print("错误")

        return messages


    async def chat_loop(self):
        """
            运行交互式聊天，允许用户输入查询并接收响应
        """
        print("\n🚀 MCP 客户端启动成功！")
        print("请输入你的查询内容（输入 'q' 退出）")

        messages = []
        while True:
            try:
                query = input("\n👤你：").strip()
                messages.append({
                    "role": "user",
                    "content": query
                })
                # 用户输入q时终止
                if query.lower() == 'q':
                    break
                messages = await self.process_query(messages)
                print("*" * 50)
                for itm in messages:
                    print(itm)
                print("*" * 50)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """清理"""
        await self.exit_stack.aclose()


async def main():
    # if len(sys.argv) < 2:
    #     print("Usage: python client.py <path_to_server_script>")
    #     sys.exit(1)
    # client = MCPClient()
    # try:
    #     print("开始连接服务器...")
    #     await client.connect_to_server(sys.argv[1])
    #     print("服务器连接成功！")
    #     await client.chat_loop()
    # finally:
    #     await client.cleanup()

    client = MCPClient()
    try:
        await client.connect_to_server("server.py")
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":

    asyncio.run(main())

