import requests
import uuid
import os
from html2img.html2img import HtmlToImage

def get_news_with_date():
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

    target_name = f"output_zb_{result['date']}.png"        # 目标文件/文件夹名
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
            imgdata = f'zb_{result['date']}',
            background="#f5f5f5",
            border_radius="35px",
            horizontal_padding=40
        )
        print(image_path)
    else:
        print("新闻获取失败:", result)
