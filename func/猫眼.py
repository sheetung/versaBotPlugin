import requests
import json

# 猫眼票房排行榜API
API_URL = "https://60s-api.viki.moe/v2/maoyan"

def get_maoyan_box_office():
    """
    获取猫眼票房排行榜数据
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
    
    return data["data"]["list"]

def format_maoyan_data(box_office_data):
    """
    格式化猫眼票房排行榜数据
    """
    formatted_data = []
    for item in box_office_data:
        formatted_item = {
            # "排名": item["rank"],
            "电影名称": item["movie_name"],
            "上映年份": item["release_year"],
            "票房": item["box_office_desc"]
        }
        formatted_data.append(formatted_item)
    return formatted_data

def main():
    print("正在获取猫眼票房排行榜数据...")
    box_office_data = get_maoyan_box_office()
    
    if not box_office_data:
        print("未获取到猫眼票房排行榜数据，请稍后再试。")
        return
    
    formatted_data = format_maoyan_data(box_office_data)
    
    print(f"共获取到 {len(formatted_data)} 条猫眼票房排行榜数据：")
    print('\n---\n')
    for idx, item in enumerate(formatted_data, start=1):
        print(f"{idx}. {item['电影名称']} (上映年份: {item['上映年份']}, 票房: {item['票房']})")
        print('\n---\n')

if __name__ == "__main__":
    main()