import httpx
import asyncio

async def fetch_color_image(max_retries=3):
    api_url = "https://3650000.xyz/api/?type=json&mode=3,5,7,8"
    for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(api_url)
                    if response.status_code == 200:
                        response_data = response.json()
                        if response_data.get("code") == 200:
                            return response_data.get("url")  # 返回图片的 URL
                        else:
                            error_msg = f"API 返回了非成功状态码。可能是链接无效或服务器端问题。尝试 {attempt + 1}/{max_retries}"
                    else:
                        error_msg = f"HTTP 状态码 {response.status_code}。尝试 {attempt + 1}/{max_retries}"
            except httpx.RequestError as e:
                error_msg = f"请求失败啦，稍后再试吧。尝试 {attempt + 1}/{max_retries}"
            except Exception as e:
                error_msg = f"发生未知错误: {str(e)}。尝试 {attempt + 1}/{max_retries}"
            # 如果不是最后一次尝试，等待一会儿再重试
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # 等待1秒再重试


async def main():
    image_url = await fetch_color_image()
    if image_url and image_url.startswith("http"):
        markdown_image_link = f"![Anime Image]({image_url})"  # 转换为 Markdown 格式
        print(markdown_image_link)  # 打印 Markdown 图片链接
    else:
        print(image_url,end='')  # 打印错误信息

if __name__ == "__main__":
    asyncio.run(main())