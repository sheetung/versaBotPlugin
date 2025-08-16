import requests
import os
import time
from datetime import datetime
from html2img.html2img import HtmlToImage
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries(max_retries=3, backoff_factor=1):
    """创建带有重试机制的requests会话"""
    session = requests.Session()
    retry = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def fetch_news_from_api(url, session=None, timeout=15):
    """从指定API获取新闻"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    if not session:
        session = create_session_with_retries()
        
    try:
        response = session.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"请求失败: {str(e)}"
    except ValueError as e:
        return f"JSON解析失败: {str(e)}"

def get_news_with_date():
    """获取新闻，尝试多个API作为备选"""
    # API列表，第一个失败会尝试第二个
    api_list = [
        "https://60s-api-cf.viki.moe/v2/60s",
        "http://api.suxun.site/api/sixs?type=json"
    ]
    
    session = create_session_with_retries(max_retries=2, backoff_factor=2)
    
    for api_url in api_list:
        print(f"尝试从API获取新闻: {api_url}")
        result = fetch_news_from_api(api_url, session)
        
        # 如果是错误消息，尝试下一个API
        if isinstance(result, str):
            print(f"API {api_url} 失败: {result}")
            # 切换API前等待一段时间
            time.sleep(2)
            continue
            
        # 处理第一个API的响应格式
        if api_url == api_list[0]:
            if "data" in result and "date" in result["data"] and "news" in result["data"] and "day_of_week" in result["data"]:
                date_with_week = f"{result['data']['date']} {result['data']['day_of_week']}"
                news_with_order = [f"{i+1}. {item}" for i, item in enumerate(result["data"]["news"])]
                return {"date": date_with_week, "news": news_with_order}
            else:
                print(f"API {api_url} 响应格式不正确")
                continue
                
        # 处理第二个API的响应格式
        if api_url == api_list[1]:
            if "date" in result and "news" in result:
                # 尝试获取星期信息（如果有的话）
                day_of_week = result.get("day_of_week", "")
                date_with_week = f"{result['date']} {day_of_week}".strip()
                return {"date": date_with_week, "news": result["news"]}
            else:
                print(f"API {api_url} 响应格式不正确")
                continue
    
    # 所有API都失败
    return "所有API都无法获取新闻数据"

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(BASE_DIR, 'html2img', 'tool', 'font', 'SourceHanSansSC-VF.ttf')
    wkhtmltoimage_path = "/usr/local/bin/wkhtmltoimage"
    
    # 验证wkhtmltoimage路径是否存在
    if not os.path.exists(wkhtmltoimage_path):
        print(f"错误: 未找到wkhtmltoimage，路径: {wkhtmltoimage_path}")
        exit(1)
    
    # 验证字体文件是否存在
    if not os.path.exists(font_path):
        print(f"错误: 未找到字体文件，路径: {font_path}")
        exit(1)
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.join(BASE_DIR, 'html2img', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    hti = HtmlToImage(wkhtmltoimage_path=wkhtmltoimage_path)

    # 最多尝试3次获取新闻
    max_attempts = 3
    attempt = 1
    result = None
    
    while attempt <= max_attempts and (result is None or not isinstance(result, dict)):
        print(f"第 {attempt} 次尝试获取新闻...")
        result = get_news_with_date()
        
        if not isinstance(result, dict):
            print(f"获取新闻失败: {result}")
            if attempt < max_attempts:
                print(f"{5 * attempt}秒后重试...")
                time.sleep(5 * attempt)  # 指数退避等待
            attempt += 1
    
    # 生成图片文件名
    current_time = datetime.now().strftime("%Y-%m-%d")
    target_name = f"zb_{current_time}.png"
    target_path = os.path.join(output_dir, target_name)

    # 首先检查本地是否已有当日图片
    if os.path.exists(target_path):
        print(f"本地已存在当日图片: {target_path}")
        exit(0)  # 直接退出，无需继续执行
    
    if isinstance(result, dict):
        try:
            # 拼接文本
            date_line = f" 日期：{result['date']}\n"
            news_lines = "\n".join(result['news'])
            full_text = f"{date_line}\n{news_lines}\nsheetung"

            # 生成图片
            image_path = hti.convert_text_to_image(
                text=full_text,
                width=1080,
                font_path=font_path,
                img_name=target_name,
                background="#f5f5f5",
                border_radius="35px",
                horizontal_padding=40
            )
            print(f"图片生成成功: {image_path}")
        except Exception as e:
            print(f"生成图片时出错: {str(e)}")
    else:
        print("最终失败: 无法获取有效的新闻数据")
