# _*_ coding=utf-8 _*_

from PIL import ImageGrab
import keyboard, time, os
from aip import AipOcr

APP_ID = "18789897"
API_KEY = "TXyLqG6qAQ3PI9QdP7cxZtzD"
SECRET_KEY = "D7sAjkatDyGUFGQF96eN2LgoWwSANH8g"

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def orc(filename):
    if not filename:
        return
    # 调用BaiDu api 进行文字识别
    text = client.basicAccurate(filename)  # 返回一个字典数据,识别到的内容已列表形式存储在 key 为 words_result 的值中
    # 如果识别到内容内容为空则结束执行
    if not text["words_result"]:
        print("抱歉，您截取的图片没有任何内容，请重新截取~！")
        user_input = input("请输入相应序号进行下一步的操作[0 退出程序| 1 重新截图]>>:")
        user_input.strip()
        if user_input.isdigit():
            user_input = int(user_input)
            if user_input == 0:
                return
            elif user_input == 1:
                screenshot()
            else:
                return

    # 过滤出识别到的内容
    result = text["words_result"]
    string = ""  # 设置一个变量用来存储文字内容
    for i in result:
        string += i["words"] + "\n"
    print(string)


def screenshot():
    # 获取快捷键进行截图
    print("请使用快捷键 'Alt+A' 键进行截图，'enter' 回车键保存截图\n")
    keyboard.wait(hotkey="Alt+A")
    # 将截图保存在系统的粘贴板中
    keyboard.wait(hotkey="enter")

    print("正在识别图片内容，请稍后...............\n")
    time.sleep(2)
    # 保存截图
    filename = ImageGrab.grabclipboard()
    filename.save("5.png")

    # 调用读取图片函数
    read_file("5.png")


def read_file(filename):
    with open(filename, "rb") as f:
        image = f.read()
    orc(image)


screenshot()
