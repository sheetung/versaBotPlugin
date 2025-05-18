import requests
import json

def get_kfc_text(type="json"):
    """
    获取肯德基疯狂星期四文案。

    Args:
        type: 返回数据类型，可选值为 "json" 或 "text"。默认为 "json"。

    Returns:
        如果 type 为 "json"，返回一个包含文案的字典。
        如果 type 为 "text"，返回文案字符串。
        如果请求失败，返回 None。
    """
    url = f"https://api.ahfi.cn/api/kfcv50?type={type}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        if type == "json":
            data = response.json()
            if data and data.get("code") == 200:
                return data.get("data", {}).get("copywriting")
            else:
                return None  # Or handle the error as needed, e.g., print(data.get("msg"))
        elif type == "text":
            return response.text
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None

# Example usage:
text = get_kfc_text()
if text:
    print(text)

text_as_text = get_kfc_text(type="text")
if text_as_text:
    print(text_as_text)


