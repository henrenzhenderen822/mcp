import asyncio
import json
import httpx
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from tools_fun.tool_hnnews import fetch_stories
from tools_fun.tool_lynews import get_lynews

# 创建 FastAPI 应用 和 MCP 服务器
# app = FastAPI()
mcp = FastMCP(name="hn-server")


@mcp.tool()
async def mcp_get_stories(hn_type: str="top", limit: int=5):
    '''
    获取 Hacker News 新闻
    type: 新闻类型(top,newest,ask,show,jobs)
    limit: 获取新闻的条数
    '''
    if hn_type not in ["top", "newest", "ask", "show", "jobs"]:
        print("新闻类型错误")
        raise TypeError
    stories = await fetch_stories(hn_type)
    limit = min(limit, 30)        # 限制最多30条新闻
    return stories[:limit]


@mcp.tool()
async def mcp_get_lynews(count: int=5):
    '''
    获取临沂新闻
    count: 获取新闻的条数
    '''
    count = count if count < 10 else 10   # 限制新闻数量为10
    news = get_lynews()
    return news[:count]


@mcp.tool()
def add(a: int, b: int) -> int:
    '''
    两数相加(a、b)
    '''
    return a + b


if __name__ == "__main__":
    # mcp.run()
    asyncio.run(mcp.run())
    # asyncio.run(mcp_get_lynews())

