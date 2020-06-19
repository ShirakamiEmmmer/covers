# -*- coding: utf-8 -*
import asyncio

from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
from selenium import webdriver
import os


def cover_list(up: str) -> list:
    video_page = webdriver.Firefox(executable_path="./geckodriver")
    video_page.get(f"https://www.youtube.com/channel/{up}/videos")
    video_page.execute_script("window.scrollTo(0,1000)")
    for i in video_page.find_elements_by_id("thumbnail"):
        yield i.get_attribute("href")
    video_page.quit()


async def cover_download(video_name: str, streamTime: str):
    cover_link = f"https://img.youtube.com/vi/{video_name}/maxresdefault.jpg"
    time = 0
    data = None
    ifRequest = False

    while not ifRequest and time < 5:
        try:
            data = requests.get(cover_link).content
            ifRequest = True
        except (TypeError, AttributeError):
            print("封面链接失败，尝试重新连接")
            time += 1

    if not ifRequest:
        with open("error_message.txt", "a+") as file:
            file.write(video_name + " cover error\n")
            file.close()
        return None

    with open(f"buffer/{video_name}.jpg", "wb") as code:
        code.write(data)
        code.close()

    with open(f"covers/{streamTime}.jpg", "wb") as code:
        code.write(data)
        code.close()


async def video_info(video_link: str, up: str):
    time = 0
    date = None
    soup = None
    ifRequested = False
    find_uploader = None

    while not ifRequested and time < 5:
        try:
            website = urlopen(video_link).read().decode("utf-8")
            soup = BeautifulSoup(website, "lxml")
            date = soup.find('meta', {'itemprop': 'startDate'})
            find_uploader = soup.find('div', {'class': 'yt-user-info'})
            find_uploader = find_uploader.find('a', {'class': 'yt-uix-sessionlink'})
            find_uploader = find_uploader['href']
            ifRequested = True
        except (AttributeError, requests.exceptions.ProxyError):
            print("视频信息链接失败，尝试重新连接")
            time += 1

    if not ifRequested:
        with open("error_message.txt", "a+") as file:
            file.write(video_link + " message error\n")
            file.close()
        return None

    if find_uploader != "/channel/" + up:
        return None

    if date:
        date = date['content'].replace('T', ' ').replace('+00:00', '')
        print(date)
    else:
        date = soup.find('meta', {'itemprop': 'datePublished'})
        date = date['content'] + " 00:00:00"
        print(date)
    return date


async def main():
    uploader = "UCdn5BQ06XqgXoAxIhbqw5Rg"
    if not os.path.exists("buffer"):
        os.mkdir("buffer")
    if not os.path.exists("covers"):
        os.mkdir("covers")

    for link in cover_list(uploader):
        try:
            name = link.replace("https://www.youtube.com/watch?v=", "")
        except AttributeError:
            print("列表为空，程序结束")
            break

        if os.path.exists(f"buffer/{name}.jpg"):
            print("该图片已经存在")
            continue

        date = await video_info(link, uploader)
        if date:
            await cover_download(name, date)
        else:
            continue


if __name__ == "__main__":
    asyncio.run(main())