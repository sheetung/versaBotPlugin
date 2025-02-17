import requests

def get_anime_image_url():
    api_url = "https://api.vvhan.com/api/wallpaper/acg?type=json"  # API 地址

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):  # 检查返回数据中的 success 字段
                image_url = data['url']
                return image_url
            else:
                print("API 返回失败")
                return None
        else:
            print("获取图片失败，状态码：", response.status_code)
            return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def main():
    image_url = get_anime_image_url()
    if image_url and image_url.startswith("http"):
        markdown_image_link = f"![Anime Image]({image_url})"  # 转换为 Markdown 格式
        print(markdown_image_link)  # 打印 Markdown 图片链接
    else:
        print("无法获取图片或图片链接无效",end='')  # 打印错误信息

if __name__ == "__main__":
    main()