import httpx
import asyncio
import sys
import re  # 新增正则模块用于提取数字

async def fetch_color_image(max_retries=3):
    """获取图片链接（带重试机制）"""
    api_url = "https://3650000.xyz/api/?type=json&mode=3,5,7,8"
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url)
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get("code") == 200:
                        return response_data.get("url")
                    else:
                        error_msg = f"API异常 code={response_data.get('code')} [尝试 {attempt+1}/{max_retries}]"
                else:
                    error_msg = f"HTTP {response.status_code} [尝试 {attempt+1}/{max_retries}]"
        except httpx.RequestError:
            error_msg = f"网络错误 [尝试 {attempt+1}/{max_retries}]"
        except Exception as e:
            error_msg = f"未知错误 {str(e)} [尝试 {attempt+1}/{max_retries}]"
        
        if attempt == max_retries - 1:
            return error_msg
        await asyncio.sleep(1)

async def main():
    """主函数处理参数解析和多请求逻辑"""
    # 解析请求次数参数（支持 x10、10次 等格式）
    n = 1  # 默认值
    if len(sys.argv) > 1:
        # 使用正则提取参数中的数字
        num_match = re.findall(r'\d+', sys.argv[1])
        if num_match:
            n = int(''.join(num_match))  # 合并连续数字（如 1x0 会转为 10）
            if n <= 0:
                print("警告：请求次数需>0，已重置为1")
                n = 1
            elif n >=10:
                n = 10
        else:
            print(f"无效参数 '{sys.argv[1]}'，使用默认值1")

    # 并发请求
    tasks = [fetch_color_image() for _ in range(n)]
    results = await asyncio.gather(*tasks)
    
    # 输出结果
    # print(f"\n🖼️ 共获取 {len([r for r in results if r.startswith('http')]}/{n} 张图片"
    for i, result in enumerate(results, 1):
        # prefix = "[成功]" if result.startswith("http") else "[失败]"
        # print(f"{prefix} 第{i}次结果：{result}")
        markdown_image_link = f"![图片]({result})"  # 转换为 Markdown 格式
        print(markdown_image_link)  # 打印 Markdown 图片链接

if __name__ == "__main__":
    asyncio.run(main())
