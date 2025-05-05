import requests


def event_stream():
    """ 监听 SSE 服务器 """
    url = "http://localhost:3000/sse"  # 你的 SSE 服务器地址
    headers = {"Accept": "text/event-stream"}

    with requests.get(url, headers=headers, stream=True) as response:
        for line in response.iter_lines():
            if line:
                print("收到消息:", line.decode())


if __name__ == "__main__":
    event_stream()
