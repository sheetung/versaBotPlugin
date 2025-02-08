import requests
#Microsoft copilot提交的插件
def get_anime_image_url():
    api_url = "https://api.vvhan.com/api/wallpaper/acg?type=json"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            image_url = data['url']
            return image_url
        else:
            print("获取图片失败")
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
        print(image_url)  # 打印错误信息


if __name__ == "__main__":
    main()
