import requests

def get_meal_suggestion():
    """
    获取今天吃什么的建议。

    Returns:
        str: 今天的饮食建议，如果请求失败则返回错误信息。
    """
    url = "https://zj.v.api.aa1.cn/api/eats/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        data = response.json()
        
        # 获取饮食建议
        if data.get("code") == 200:
            suggestion = data.get("mealwhat", "没有找到今天的饮食建议。")
            return f"今天吃什么？ {suggestion}"
        else:
            return f"API Error: {data.get('msg', 'Unknown error')}"
    except requests.RequestException as e:
        return f"请求失败: {str(e)}"

if __name__ == "__main__":
    print(get_meal_suggestion())
