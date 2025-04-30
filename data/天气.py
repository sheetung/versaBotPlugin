import requests
import os
import json
import sys 

def get_location_id(api_key, location_name):
    """
    通过GeoAPI获取城市的Location ID
    """
    geoapi_url = "https://geoapi.qweather.com/v2/city/lookup"
    params = {
        "key": api_key,
        "location": location_name
    }
    response = requests.get(geoapi_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == "200":
            # 获取Location ID
            location_id = data["location"][0]["id"]
            return location_id
        else:
            print(f"GeoAPI错误：{data.get('code')}, {data.get('message')}")
    else:
        print(f"GeoAPI请求失败，状态码：{response.status_code}")
    return None

def get_realtime_weather(api_key, location_id):
    """
    获取实时天气
    """
    url = "https://api.qweather.com/v7/weather/now"
    params = {
        "key": api_key,
        "location": location_id
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_forecast_weather(api_key, location_id):
    """
    获取未来三天天气预报
    """
    url = "https://api.qweather.com/v7/weather/3d"
    params = {
        "key": api_key,
        "location": location_id
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def main():
    try:
        # 获取脚本所在目录的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'weather_key.json')
        # 从 config.json 读取 token
        with open(config_path, 'r') as f:
            config = json.load(f)
            api_key = config['apikey']
    except FileNotFoundError:
        print("错误：当前目录未找到 config.json 文件", end='')
    except json.JSONDecodeError:
        print("错误：config.json 格式不正确", end='')
    except KeyError:
        print("错误：config.json 缺少 token 字段", end='')
    
    city_name = sys.argv[1] if len(sys.argv) > 1 else "贵阳"
    # 获取Location ID
    location_id = get_location_id(api_key, city_name)
    if not location_id:
        print(f'无法获取城市的位置信息，请检查城市名称{city_name}是否正确。')
        return
    
    # 获取实时天气和未来三天天气预报
    realtime_weather = get_realtime_weather(api_key, location_id)
    forecast_weather = get_forecast_weather(api_key, location_id)
    
    if realtime_weather and forecast_weather:
        now = realtime_weather['now']
        print(f"📍 城市：{city_name}")
        print("-"*7)
        print(f"🌤 实时天气：{now['text']}")
        print(f"🌡 当前温度：{now['temp']}℃")
        print(f"💨 风力：{now['windDir']} {now['windScale']}级")
        print(f"💧 湿度：{now['humidity']}%")
        print("📅 未来三天天气预报：")
        for day in forecast_weather['daily']:
            print(f"日期：{day['fxDate']}")
            print(f"☀白天：{day['textDay']}，🌙夜间：{day['textNight']}")
            print(f"🔺最高温度：{day['tempMax']}℃，🔻最低温度：{day['tempMin']}℃")
    else:
        print("❌ 获取天气数据失败，请检查网络或API配置。")

if __name__ == "__main__":
    main()