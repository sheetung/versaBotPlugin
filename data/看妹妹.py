import httpx
import asyncio

async def fetch_color_image():
    api_url = "https://3650000.xyz/api/?type=json&mode=3"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("code") == 200:
                    return response_data.get("url")  # 返回图片的 URL
                else:
                    return f"API 返回了非成功状态码。可能是链接无效或服务器端问题。"
            else:
                return None
    except httpx.RequestError as e:
        return ("请求失败啦，稍后再试吧\n")
    except Exception as e:
        return f"发生未知错误: {str(e)}"


async def main():
    image_url = await fetch_color_image()
    if image_url and image_url.startswith("http"):
        markdown_image_link = f"![Anime Image]({image_url})"  # 转换为 Markdown 格式
        print(markdown_image_link)  # 打印 Markdown 图片链接
    else:
        print(image_url)  # 打印错误信息

if __name__ == "__main__":
    asyncio.run(main())