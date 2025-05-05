import json
import requests
from bs4 import BeautifulSoup
import re
from pypinyin import lazy_pinyin


def get_weather(location):
    """ 解析网页，提取 JSON-LD 中的 `description` 字段 """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                      " (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    city = "".join(lazy_pinyin(location))

    # 示例: 天气网北京天气页面
    url = f"https://www.tianqi.com/{city}/"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    # print(soup)

    # 提取温度
    temperature = ""
    temperature_tag = soup.find("p", class_="now")
    if temperature_tag:
        temperature = temperature_tag.text.strip()
    # print(temperature)

    # 提取天气状况
    weather_condition = ""
    span_tag = soup.find_all("span")
    for span in span_tag:
        weather_tag = span.find("b")
        if weather_tag:
            weather_condition = weather_tag.text.strip()
    # print(weather_condition)

    # 提取湿度信息
    humidity_info = ""
    humidity_tag = soup.find("dd", class_="shidu")
    b_tag = humidity_tag.find_all("b")
    for b in b_tag:
        humidity_info = humidity_info + b.text.strip() + " "
    # print(humidity_info)

    return str("温度：" + temperature + " 天气状况：" + weather_condition + " " + humidity_info)


if __name__ == '__main__':

    description = get_weather("北京")
    print("天气状况如下")
    print(description)
