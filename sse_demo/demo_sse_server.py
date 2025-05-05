from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
from datetime import datetime

app = FastAPI()


async def event_generator(request: Request):
    """SSE 事件生成器，带计数器（counter）"""
    counter = 0
    try:
        while True:
            if await request.is_disconnected():
                break  # 客户端断开连接时停止

            if counter > 20:
                # 发送关闭事件（模仿 Node.js 的 event:close）
                yield "event: close\n"
                yield "data: close\n\n"
                break

            # 发送计数器数据
            yield f"data: {counter}\n\n"
            counter += 1
            await asyncio.sleep(0.1)  # 100ms 间隔（模仿 Node.js 的 setInterval(100)）

    except asyncio.CancelledError:
        print("客户端断开连接")


@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE 接口"""
    return StreamingResponse(
        event_generator(request),
        media_type="text/event-stream",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)


