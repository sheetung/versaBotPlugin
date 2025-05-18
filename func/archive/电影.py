# from bs4 import BeautifulSoup
# import requests
# import re
# import sys
# import time
# from urllib.parse import urljoin, quote

# BASE_URL = "https://anybt.eth.limo"
# HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# }


# def get_all_products(keyword):
#     try:
#         encoded_keyword = quote(keyword)
#         search_url = urljoin(BASE_URL, f"#/search?q={encoded_keyword}&order=&category=")
#         response = requests.get(search_url, headers=HEADERS)
#         response.raise_for_status()
#         time.sleep(5)
#     except Exception as e:
#         print(f"请求失败: {e}")
#         return []

#     soup = BeautifulSoup(response.text, 'html.parser')
#     all_products = []
#     # 假设电影列表项的 CSS 选择器，需根据实际页面调整
#     movie_containers = soup.select('div.movie-item')

#     for container in movie_containers:
#         # 提取电影名字
#         name_element = container.find('h2')
#         if not name_element:
#             continue
#         movie_name = name_element.get_text(strip=True)

#         # 提取详情链接
#         a_tag = container.find('a')
#         if not a_tag or not a_tag.get('href'):
#             continue
#         detail_link = urljoin(BASE_URL, a_tag['href'])

#         # 提取大小，假设大小信息在某个特定 class 的元素中，需根据实际调整
#         size_element = container.find('span', class_='size')
#         movie_size = size_element.get_text(strip=True) if size_element else '未知'

#         # 提取下载链接，假设下载链接在某个特定 class 的元素中，需根据实际调整
#         download_element = container.find('a', class_='download')
#         download_link = urljoin(BASE_URL, download_element['href']) if download_element else '无'

#         all_products.append({
#             "电影名字": movie_name,
#             "详情链接": detail_link,
#             "大小": movie_size,
#             "下载链接": download_link
#         })

#     # return all_products
#     return soup


# def main():
#     # 命令行参数处理（默认搜索词为 "电影"）
#     keyword = sys.argv[1] if len(sys.argv) > 1 else "电影"
#     matched_products = get_all_products(keyword)
#     print(f'result::{matched_products}')
#     if not matched_products:
#         encoded_keyword = quote(keyword)
#         print(f"未找到包含 '{keyword}' 的电影\n可到页面查询:{urljoin(BASE_URL, f"#/search?q={encoded_keyword}&order=&category=")}")
#         print('\n---\n')
#     else:
#         print(f"共找到包含 {keyword} 的 {len(matched_products)} 个匹配电影，更多电影请到页面查询:https://anybt.eth.limo/#/search?q={keyword}&order=&category=")
#         print('\n---\n')

#         # 提取并展示详细信息，只取前 5 个结果
#         results = matched_products[:5]
#         for data in results:
#             for key, value in data.items():
#                 print(f"{key}: {value}")
#             print('\n---\n')


# if __name__ == "__main__":
#     main()
    
from bs4 import BeautifulSoup
import requests
import sys
from urllib.parse import urljoin

BASE_URL = "https://anybt.eth.limo"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def get_all_products(keyword):
    try:
        search_url = urljoin(BASE_URL, f"#/search?q={keyword}&order=&category=")
        response = requests.get(search_url, headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"请求失败: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    all_products = []
    # 调整选择器以匹配实际结构
    movie_containers = soup.select('div.search-result-item')
    for container in movie_containers:
        # 提取电影名字
        name_element = container.find('mark')
        movie_name = name_element.get_text(strip=True) if name_element else '未知'
        # 提取大小
        size_element = container.find('span', class_='ant - tag')
        size = size_element.get_text(strip=True) if size_element else '未知'
        # 提取日期
        date_element = container.select('span.ant - tag')[1] if len(container.select('span.ant - tag')) > 1 else None
        date = date_element.get_text(strip=True) if date_element else '未知'
        # 提取磁力链接
        magnet_element = container.find('a', href=lambda x: x and x.startswith('magnet:'))
        magnet_link = magnet_element['href'] if magnet_element else '无'

        all_products.append({
            "电影名字": movie_name,
            "大小": size,
            "日期": date,
            "磁力链接": magnet_link
        })

    return soup


def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else "流浪地球2"
    matched_products = get_all_products(keyword)
    print(f'result::{matched_products}')
    if not matched_products:
        print(f"未找到包含 '{keyword}' 的电影\n可到页面查询:https://anybt.eth.limo/#/search?q={keyword}&order=&category=")
        print('\n---\n')
    else:
        for data in matched_products:
            for key, value in data.items():
                print(f"{key}: {value}")
            print('\n---\n')


if __name__ == "__main__":
    main()