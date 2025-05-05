import asyncio
import json
import httpx
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP


# Hacker News 主页 URL
BASE_URL = "https://news.ycombinator.com"


# 定义新闻故事的结构
class Story:
    def __init__(self, title: str, url: Optional[str], points: int, author: str, time: str, comment_count: int,
                 rank: int):
        self.title = title
        self.url = url
        self.points = points
        self.author = author
        self.time = time
        self.comment_count = comment_count
        self.rank = rank

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "points": self.points,
            "author": self.author,
            "time": self.time,
            "comment_count": self.comment_count,
            "rank": self.rank,
        }


async def fetch_stories(story_type: str = "top") -> List:
    """从 Hacker News 抓取指定类型的新闻故事"""
    # try:
    url = BASE_URL if story_type == "top" else f"{BASE_URL}/{story_type}"
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    stories = []

    # 解析 HTML 并提取文章信息
    for i, item in enumerate(soup.select(".athing")):
        title_elem = item.select_one(".titleline > a")
        title = title_elem.text.strip() if title_elem else "Unknown"
        url = title_elem["href"] if title_elem and title_elem.has_attr("href") else None
        metadata = item.find_next_sibling()

        points = int(metadata.select_one(".score").text.strip().split()[0]) if metadata.select_one(".score") else 0
        author = metadata.select_one(".hnuser").text.strip() if metadata.select_one(".hnuser") else "Unknown"
        time = metadata.select_one(".age")["title"] if metadata.select_one(".age") else "Unknown"
        comments_elem = metadata.select("a")[-1]
        try:
            comment_count = int(comments_elem.text.split()[0])
        except:
            comment_count = 0

        stories.append(Story(title, url, points, author, time, comment_count, i+1).to_dict())

    return stories


if __name__ == '__main__':
    stories = asyncio.run(fetch_stories())
    print(json.dumps(stories, indent=2))

