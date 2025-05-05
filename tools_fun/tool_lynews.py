import requests
from bs4 import BeautifulSoup


def get_lynews():
    # 目标 URL
    url = f"http://www.lytoday.com/jrly/lyxw/node_111.htm"

    # 伪装请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    # print(soup)
    news_span = soup.find_all('div', class_='wz_list_box lin16')
    # print(news_span)
    result = []
    for itm in news_span:
        result.append(itm.getText(strip=True))

    return result


if __name__ == '__main__':
    print(get_lynews())

