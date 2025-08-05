import os
import subprocess
import uuid
import re  # 用于文件名校验
from PIL import Image

class HtmlToImage:
    def __init__(self, wkhtmltoimage_path='/usr/local/bin/wkhtmltoimage'):
        self.wkhtmltoimage_path = wkhtmltoimage_path
        if not os.path.exists(self.wkhtmltoimage_path):
            raise FileNotFoundError(f"{self.wkhtmltoimage_path} not found.")

    def _generate_html(self, text, font_path, font_name, width=600, background="#ffffff", border_radius="16px", horizontal_padding=40):
        font_path_web = font_path.replace("\\", "/")
        content_width = width - horizontal_padding * 2  
        paragraphs = [p.strip() for p in text.strip().split("\n") if p.strip()]
        paragraph_html = ""

        for i, para in enumerate(paragraphs):
            if i == 0:
                paragraph_html += f"<p class='first'>{para}</p>"
                paragraph_html += "<hr class='separator'>"
            elif i == len(paragraphs) - 1:
                paragraph_html += f"<p class='last'>{para}</p>"
            else:
                paragraph_html += f"<p>{para}</p>"
                paragraph_html += "<hr class='separator'>"

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @font-face {{
                    font-family: '{font_name}';
                    src: url('{font_path_web}');
                }}
                html, body {{
                    margin: 0;
                    padding: 0;
                    background: transparent;
                }}
                .container {{
                    width: {content_width}px;
                    padding: 40px {horizontal_padding}px;
                    background-color: {background};
                    border-radius: {border_radius};
                    box-shadow: 0 0 32px rgba(0,0,0,0.08);
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-family: '{font_name}', 'Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji', 'Symbola', sans-serif;
                    font-size: 50px;
                    line-height: 1.6;
                }}
                p {{
                    margin: 0;
                    margin-top: 0;
                    padding-bottom: 10px;
                }}
                p.first {{
                    font-weight: bold;
                    text-align: center;
                }}
                p.last {{
                    color: #999999;
                    text-align: right;
                }}
                hr.separator {{
                    border: 1px solid #e0e0e0;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">{paragraph_html}</div>
        </body>
        </html>
        """
        return html_template


    def convert_text_to_image(self, text, font_path, img_name, output_path=None, width=None, background="#ffffff", border_radius="16px",horizontal_padding=40, quality=60):
        """
        核心逻辑不变，新增：
        1. 文件名合法性校验（解决“无效结果格式”警告）
        2. 兼容网络异常场景（虽然本函数不涉及网络，但调用方可能有，需规范错误传递）
        """
        # ================= 新增：文件名校验 =================
        # 过滤非法字符，避免触发默认错误文件名
        valid_img_name = re.sub(r'[^\w\.-]', '_', img_name)  
        if not valid_img_name.lower().endswith('.png'):
            valid_img_name += '.png'
        img_name = valid_img_name

        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")

        font_name = os.path.splitext(os.path.basename(font_path))[0]

        if width is None:
            estimated_width = min(600, max(300, len(text) * 15))  
            width = estimated_width

        html_content = self._generate_html(
            text, font_path, font_name, width, background, border_radius, horizontal_padding
        )
        html_file = f"temp_{uuid.uuid4().hex}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        if output_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(base_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, img_name)

        command = [
            self.wkhtmltoimage_path,
            "--enable-local-file-access",
            "--encoding", "utf-8",
            "--disable-smart-width",
            "--width", str(width),
            "--quality", str(quality),  
            html_file,
            output_path
        ]

        try:
            subprocess.run(command, check=True)
            if quality < 100:  
                with Image.open(output_path) as img:
                    img.save(output_path, quality=quality, optimize=True)
        except subprocess.CalledProcessError as e:
            os.remove(html_file)
            # 保持原错误抛出逻辑
            raise RuntimeError("wkhtmltoimage failed") from e

        os.remove(html_file)
        return output_path

# 示例用法（main 函数仅作演示，实际由其他脚本调用时无需关注）
if __name__ == "__main__":
    font_path = os.path.join('html2img', 'tool', 'font', 'SourceHanSansSC-VF.ttf')
    wkhtmltoimage_path = os.path.abspath(os.path.join("D:", "wkhtmltox", "bin", "wkhtmltoimage.exe"))
    hti = HtmlToImage(wkhtmltoimage_path=wkhtmltoimage_path)
    
    try:
        result = hti.convert_text_to_image(
            text=f"""
            2025年02月12日 星期一\n
            你好，这是使用自定义字体渲染的文字支持多行显示，自动高度适配。\n
            sheetung\n
            """,
            width = 1080,
            font_path=font_path,
            img_name="测试文件名.png",  # 可观察文件名过滤效果
            background="#f5f5f5",
            border_radius="35px",
            horizontal_padding = 40
        )
        print("图片生成成功:", result)
    except Exception as e:
        # 这里可捕获调用方的网络异常（如其他脚本请求新闻时的 ConnectionResetError）
        print(f"执行失败: {str(e)}")