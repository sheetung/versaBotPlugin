import requests
import json
from urllib.parse import urljoin

# 微博热搜榜API
API_URL = "https://60s-api.viki.moe/v2/weibo"

def get_weibo_hot_search():
    """
    获取微博热搜榜数据
    """
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
    except Exception as e:
        print(f"请求失败: {e}")
        return []
    
    data = response.json()
    if data["code"] != 200:
        print(f"API返回错误: {data.get('message', '未知错误')}")
        return []
    
    return data["data"]

def format_hot_search_data(hot_search_data):
    """
    格式化微博热搜榜数据
    """
    formatted_data = []
    for item in hot_search_data:
        formatted_item = {
            "热搜词": item["title"],
            "热度": item["hot_value"],
            "详情链接": urljoin("https://s.weibo.com", item["link"])
        }
        formatted_data.append(formatted_item)
    return formatted_data

def main():
    print("正在获取微博热搜榜数据...")
    hot_search_data = get_weibo_hot_search()
    
    if not hot_search_data:
        print("未获取到微博热搜榜数据，请稍后再试。")
        return
    
    formatted_data = format_hot_search_data(hot_search_data)
    
    print(f"共获取到 {len(formatted_data)} 条微博热搜数据：")
    print('\n---\n')
    for idx, item in enumerate(formatted_data, start=1):
        print(f"{idx}. {item['热搜词']} (热度: {item['热度']})")
        print(f"   详情链接: {item['详情链接']}")
        print('\n---\n')

if __name__ == "__main__":
    main()