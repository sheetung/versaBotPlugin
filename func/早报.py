import requests
import uuid
import os
from html2img.html2img import HtmlToImage

def get_news_with_date_old():
    url = "http://api.suxun.site/api/sixs"
    params = {"type": "json"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 检查HTTP状态码
        
        data = response.json()
        
        if "date" in data and "news" in data:
            return {
                "date": data["date"],
                "news": data["news"]
            }
        else:
            return "响应中缺少日期或新闻字段"
            
    except requests.exceptions.RequestException as e:
        return f"请求失败: {e}"
    except ValueError as e:
        return f"JSON解析失败: {e}"

def get_news_with_date():
    # 修改API URL
    url = "https://60s-api-cf.viki.moe/v2/60s"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查HTTP状态码
        
        data = response.json()
        
        if "data" in data and "date" in data["data"] and "news" in data["data"] and "day_of_week" in data["data"]:
            # 拼接日期和星期
            date_with_week = f"{data['data']['date']} {data['data']['day_of_week']}"
            news_with_order = []
            for index, news_item in enumerate(data["data"]["news"], 1):
                news_with_order.append(f"{index}. {news_item}")
            return {
                "date": date_with_week,
                "news": news_with_order
            }
        else:
            return "响应中缺少日期、新闻或星期字段"
            
    except requests.exceptions.RequestException as e:
        return f"请求失败: {e}"
    except ValueError as e:
        return f"JSON解析失败: {e}"

# 使用示例
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(BASE_DIR,'html2img', 'tool', 'font', 'SourceHanSansSC-VF.ttf')
    wkhtmltoimage_path = "/usr/local/bin/wkhtmltoimage"
    hti = HtmlToImage(wkhtmltoimage_path=wkhtmltoimage_path)

    result = get_news_with_date()
    
    # if isinstance(result, dict):
    #     print(f"📅 日期：{result['date']}\n")
    #     for index, news_item in enumerate(result["news"], 1):
    #         print(f"{news_item}")
    # else:
    #     print(result)  # 输出错误信息

    # target_name = f"zb_{result['date'][:10]}.png"        # 目标文件/文件夹名
    if isinstance(result, dict) and "date" in result:
        # 截取前10位确保日期格式（如2025-06-29）
        date_str = result["date"][:10]
        target_name = f"zb_{date_str}.png"
    else:
        # 异常情况使用UUID避免文件名重复
        target_name = f"zb_error_{uuid.uuid4().hex[:8]}.png"
        print(f"警告：无效的结果格式，使用默认文件名 {target_name}")
    target_path = os.path.join(BASE_DIR, 'html2img', 'output', target_name)
    # 判断是否已经生成
    if os.path.exists(target_path):
        print(target_path)

    elif isinstance(result, dict):
        # 拼接文本
        date_line = f"📅 日期：{result['date']}\n"
        news_lines = "\n".join(result['news'])
        full_text = f"{date_line}\n{news_lines}\nsheetung"

        # 生成图片
        image_path = hti.convert_text_to_image(
            text=full_text,
            width=1080,
            font_path=font_path,
            img_name = target_name,
            background="#f5f5f5",
            border_radius="35px",
            horizontal_padding=40
        )
        print(image_path)
    else:
        print("新闻获取失败:", result)
