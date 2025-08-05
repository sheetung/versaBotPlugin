from bs4 import BeautifulSoup
import requests
import re
import sys
from urllib.parse import urljoin

BASE_URL = "https://172.lot-ml.com"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 国内省份列表（包含全称和简称）
PROVINCES = [
    "北京市", "北京", "天津市", "天津", "河北省", "河北", "山西省", "山西",
    "内蒙古自治区", "内蒙古", "辽宁省", "辽宁", "吉林省", "吉林", "黑龙江省", "黑龙江",
    "上海市", "上海", "江苏省", "江苏", "浙江省", "浙江", "安徽省", "安徽",
    "福建省", "福建", "江西省", "江西", "山东省", "山东", "河南省", "河南",
    "湖北省", "湖北", "湖南省", "湖南", "广东省", "广东", "广西壮族自治区", "广西",
    "海南省", "海南", "重庆市", "重庆", "四川省", "四川", "贵州省", "贵州",
    "云南省", "云南", "西藏自治区", "西藏", "陕西省", "陕西", "甘肃省", "甘肃",
    "青海省", "青海", "宁夏回族自治区", "宁夏", "新疆维吾尔自治区", "新疆",
    "香港特别行政区", "香港", "澳门特别行政区", "澳门", "台湾省", "台湾"
]

def get_all_products(keyword):
    # 判断关键词类型并选择对应的页面路径
    # 检查是否为数字类型关键词（包含数字）
    is_number = bool(re.search(r'\d', keyword))
    # 检查是否为省份关键词（不区分大小写）
    keyword_lower = keyword.lower()
    is_province = any(p.lower() == keyword_lower for p in PROVINCES)
    
    # 根据关键词类型选择不同的页面
    if is_province:
        path = "/producten/tyindex/3abcd2e80b9b4694"
        # print(f"检测到省份关键词，使用省份专属页面: {path}")
    elif is_number:
        path = "/ProductEn/Index/3abcd2e80b9b4694"
        # print(f"检测到数字类型关键词，使用数字专属页面: {path}")
    else:
        # 其他情况默认使用原页面
        path = "/ProductEn/Index/3abcd2e80b9b4694"
        # print(f"使用默认页面: {path}")
    
    try:
        response = requests.get(urljoin(BASE_URL, path), headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"请求失败: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    all_products = []
    seen_links = set()
    seen_names = set()  # 名称去重容器
    
    # 精确锁定产品列表（根据实际页面结构调整选择器）
    product_containers = soup.select('div.new_lst')
    
    for container in product_containers:
        for li in container.select('ul.fa > li'):
            h1 = li.find('h1')
            if not h1:
                continue
            
            # 名称模糊匹配
            product_name = h1.get_text(strip=True)
            if not re.search(re.escape(keyword), product_name, re.I):
                continue
            
            # 关键去重逻辑
            if product_name in seen_names:
                continue
            seen_names.add(product_name)
            
            # 链接处理
            a_tag = li.find('a')
            if not a_tag or not a_tag.get('href'):
                continue
            detail_link = urljoin(BASE_URL, a_tag['href'])
            if detail_link in seen_links:
                continue
            seen_links.add(detail_link)
            
            all_products.append({
                "element": li,
                "detail_link": detail_link
            })
    
    return all_products

# 数据提取函数
def extract_product_data(product_li):
    # 提取基础信息
    img_tag = product_li.find('dt').find('img')
    product_name = product_li.find('h1').get_text(strip=True)
    
    # 处理主推/年龄/领取人数
    b1_div = product_li.find('div', class_='b1')
    zhutui = '是' if b1_div.find('span', class_='zhutui') else '否'
    age_span = b1_div.find('span', class_='xl')
    receive_span = b1_div.find('span', class_='yr')
    
    # 流量信息处理
    flow_data = {"通用流量": "0G", "定向流量": "0G", "通话时长": "0分钟"}
    b2_div = product_li.find('div', class_='b2')
    if b2_div:
        for span in b2_div.find_all('span'):
            text = span.get_text(strip=True)
            if '通用流量' in text:
                flow_data['通用流量'] = text.split()[-1]
            elif '定向流量' in text:
                flow_data['定向流量'] = text.split()[-1]
            elif '通话时长' in text:
                flow_data['通话时长'] = text.split()[-1]
    
    return {
        "md图片":f"![图片]({urljoin(BASE_URL, img_tag['src']) if img_tag else None})",
        "产品名称": product_name,
        **flow_data
    }

def main():
    # 命令行参数处理（默认搜索词为"19元"）
    keyword = sys.argv[1] if len(sys.argv) > 1 else "19元"
    matched_products = get_all_products(keyword)

    if not matched_products:
        print(f"未找到包含 '{keyword}' 的产品\n可到页面店铺查询:https://172.lot-ml.com/ProductEn/Index/3abcd2e80b9b4694")
        print('\n---\n')
    else:
        print(f"共找到包含{keyword}的 {len(matched_products)} 个匹配产品，更多流量卡请到页面店铺查询:https://172.lot-ml.com/ProductEn/Index/3abcd2e80b9b4694")
        print('\n---\n')
        
        # 提取并展示详细信息
        results = []
        for product in matched_products:
            data = extract_product_data(product["element"])
            data["详情链接"] = product["detail_link"]
            results.append(data)
            
            # 打印单条结果
            for key, value in data.items():
                if key == "md图片":
                    print(value,end='\n')
                    continue
                print(f"{key}: {value}")
            print('\n---\n')

if __name__ == "__main__":
    main()
