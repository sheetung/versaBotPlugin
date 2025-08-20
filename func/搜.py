from bs4 import BeautifulSoup
import requests
import re
import sys
from urllib.parse import urljoin

# 用于获取 search.json 数据的基础链接
BASE_SEARCH_URL = "https://blog.afei7.com"  
SEARCH_JSON_PATH = "/search.json"  
ARTICLE_BASE_URL = "https://blog.afei7.com"  

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 可扩展的近义词表，用于辅助匹配（根据需求添加）
SYNONYMS = {
    "铁血战士": ["终极战士", "Predator"],
    "杀戮之王": ["杀手之王", "Killer of Killers"]
}

def get_search_data():
    """获取 search.json 数据"""
    try:
        response = requests.get(urljoin(BASE_SEARCH_URL, SEARCH_JSON_PATH), headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"请求 search.json 失败: {e}")
        return []

def search_and_match(keyword):
    """优化模糊匹配逻辑，结合标题和内容，支持近义词"""
    search_data = get_search_data()
    if not search_data:
        return []

    results = []
    seen_combinations = set()  # 用标题+链接的组合去重，更精准

    # 拆分关键词，生成包含近义词的匹配词列表
    match_words = [keyword]
    for part in keyword.split():
        if part in SYNONYMS:
            match_words.extend(SYNONYMS[part])

    for item in search_data:
        title = item.get("title", "").lower()
        content = item.get("content", "").lower()
        article_url = urljoin(ARTICLE_BASE_URL, item.get("uri", ""))

        # 标题或内容中包含任意匹配词即视为匹配
        is_match = any(
            re.search(re.escape(word.lower()), title) or 
            re.search(re.escape(word.lower()), content) 
            for word in match_words
        )
        if not is_match:
            continue

        # 组合去重（标题+链接）
        unique_key = f"{title}|{article_url}"
        if unique_key in seen_combinations:
            continue
        seen_combinations.add(unique_key)

        results.append({
            "element": item,
            "article_url": article_url
        })

    return results

def extract_article_info(article_item):
    """提取文章内特定容器的目标图片、磁力链接等信息"""
    article_url = article_item["article_url"]
    try:
        response = requests.get(article_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 精准匹配目标图片所在容器及图片（根据你提供的结构，锁定 article 下的 lightgallery 里的 img）
        target_img = None
        lightgallery_a = soup.select_one('article.page.single a.lightgallery')
        if lightgallery_a:
            target_img = lightgallery_a.find('img', loading='lazy', alt='海报')
        img_url = target_img.get('src') if target_img else ""

        # 提取磁力链接（优化正则，支持更多格式）
        magnet_links = re.findall(
            r'magnet:\?xt=urn:btih:[a-fA-F0-9]{40}(?:&dn=[^&]+)?(?:&tr=[^&]+)*', 
            response.text
        )

        return {
            "标题": article_item["element"].get("title", ""),
            "海报图片链接": [img_url] if img_url else [],
            "磁力链接": magnet_links
        }
    except Exception as e:
        return {
            "海报图片链接": [],
            "磁力链接": []
        }

def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else " "
    matched_items = search_and_match(keyword)

    if not matched_items:
        print(f"未找到包含 '{keyword}' 的内容")
        print('\n---\n')
    else:
        print(f"共找到包含 {keyword} 的 {len(matched_items)} 条匹配内容")
        print('\n---\n')

        for idx, item in enumerate(matched_items, start=1):
            article_info = extract_article_info(item)
            # 打印结果
            print(f"第 {idx} 条结果")
            for key, value in article_info.items():
                if key == "磁力链接":
                    for mag_idx, mag_link in enumerate(value, start=1):
                        print(f"  {key} {mag_idx}: {mag_link}")  # 截断长链接，保持整洁
                else:
                    print(f"  {key}: {value}")
            print('\n---\n')

if __name__ == "__main__":
    main()