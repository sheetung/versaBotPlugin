import requests

def get_news_with_date():
    url = "http://api.suxun.site/api/sixs"
    params = {"type": "json"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 检查HTTP状态码
        
        data = response.json()
        
        if "date" in data and "news" in data:
            return {
                "date": data["date"],
                "news": data["news"]
            }
        else:
            return "响应中缺少日期或新闻字段"
            
    except requests.exceptions.RequestException as e:
        return f"请求失败: {e}"
    except ValueError as e:
        return f"JSON解析失败: {e}"

# 使用示例
if __name__ == "__main__":
    result = get_news_with_date()
    
    if isinstance(result, dict):
        print(f"📅 日期：{result['date']}\n")
        for index, news_item in enumerate(result["news"], 1):
            print(f"{news_item}")
    else:
        print(result)  # 输出错误信息
