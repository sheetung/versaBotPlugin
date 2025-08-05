import os

def get_py_files(directory):
    """获取指定目录下的所有.py文件，排除菜单本身"""
    py_files = []
    for file in os.listdir(directory):
        if file.endswith('.py') and file != '菜单.py' and file != '__init__.py':  # 排除菜单本身
            py_files.append(file)
    return py_files

def generate_menu(py_files):
    """生成菜单输出"""
    menu = []
    for index, file in enumerate(py_files, start=1):
        # 去掉.py扩展名，作为菜单项名称
        menu_item = os.path.splitext(file)[0]
        menu.append(f"{index}. <{menu_item}>")
    menu.append(f"{index+1}. <{'打卡'}>")
    menu.append(f"{index+2}. <{'赞我'}>")
    # return "\n".join(menu)
    return "/home/sheetung/LangBotV4.0/plugins/versaBotPlugin/func/img/menu.png"

async def main():
    directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
    py_files = get_py_files(directory)
    if not py_files:
        print("当前目录下没有找到其他.py插件文件。")
    else:
        menu = generate_menu(py_files)
        print(menu)
        print("---")
        print("输入 <任意功能名> 唤醒我~")
        print("要跟我对话，'ai'前缀唤醒我~",end='')

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())