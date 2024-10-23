import sys
# sys.path.insert(0, './packages')
import cv2
from modules.load_config import load_config
from modules.send_sign_in_threading import send_sign_in_threading



def handler(event, context):
    print(cv2.__file__)
        
    # 加载配置信息
    users = load_config()
    # 传入配置信息, 启动项目
    send_sign_in_threading(users)


# ❗1. 开发环境时解除下方的handler(0, 0)用于启动主程序
# ❗2. Github云函数需要保留这一行
# ❗3. 华为云函数需要注释这一行, 否则会连续运行2次打卡任务
# 开发环境时请解除下方注释, 但是请注意在部署时要注释或移除这行, 因为云函数会自动运行一次handler, 不注释掉会造成连续推送2次
handler(0, 0)
