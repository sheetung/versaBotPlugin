import httpx
import asyncio

async def fetch_color_image():
    api_url = "http://3650000.xyz/api/?type=json&mode=7"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("code") == 200:
                    return response_data.get("url")  # 返回图片的 URL
                else:
                    return "API 返回了非成功状态码。可能是链接无效或服务器端问题。"
            else:
                return f"请求失败，状态码: {response.status_code}。可能是网络问题或链接无效。"
    except httpx.RequestError as e:
        return ("请求失败啦，稍后再试吧\n")
    except Exception as e:
        return f"发生未知错误: {str(e)}"

async def main():
    image_url = await fetch_color_image()
    if image_url:
        markdown_image_link = f"![Anime Image]({image_url})"  # 转换为 Markdown 格式
        print(markdown_image_link)  # 打印 Markdown 图片链接
    else:
        print("可能这张图被吞了~再试试吧")  # 提示没有找到图片

if __name__ == "__main__":
    asyncio.run(main())
