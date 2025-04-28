import requests
import json
import os

def get_zaobao_image_url(token):
    api_url = "https://v3.alapi.cn/api/zaobao"  # API 地址
    params = {
        "token": token,
        "format": "json"  # 指定返回格式为 JSON
    }
    headers = {"Content-Type": "application/json"}  # 设置请求头

    try:
        response = requests.post(api_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                # 获取图片 URL
                image_url = data.get("data", {}).get("image")
                if image_url:
                    return image_url
                else:
                    print("未找到图片 URL")
                    return None
            else:
                print(f"API 返回错误：{data.get('msg')}")
                return None
        else:
            print(f"获取图片失败，状态码：{response.status_code}")
            return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def main():
    try:
         # 获取脚本所在目录的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'zaobao_token.json')

        # 从 config.json 读取 token
        with open(config_path, 'r') as f:
            config = json.load(f)
            token = config['token']
            # token = ''
        
        # 获取图片 URL
        image_url = get_zaobao_image_url(token)
        
        if image_url and image_url.startswith("http"):
            markdown_image_link = f"![早报图片]({image_url})"  # 转换为 Markdown 格式
            print(markdown_image_link)  # 打印 Markdown 图片链接
        else:
            print("获取图片失败或链接无效", end='')
    except FileNotFoundError:
        print("错误：当前目录未找到 config.json 文件", end='')
    except json.JSONDecodeError:
        print("错误：config.json 格式不正确", end='')
    except KeyError:
        print("错误：config.json 缺少 token 字段", end='')

if __name__ == "__main__":
    main()