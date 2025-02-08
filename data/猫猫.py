import requests
#Microsoft copilot提交的插件
def get_cat_image_url():
    api_url = "https://api.thecatapi.com/v1/images/search?limit=1"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            image_url = data[0]['url']
            return image_url
        else:
            print("获取图片失败")
            return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def main():
    image_url = get_cat_image_url()
    if image_url:
        markdown_image_link = f"![Cat Image]({image_url})"
        print(markdown_image_link)

if __name__ == "__main__":
    main()
