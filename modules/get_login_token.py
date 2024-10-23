import json, time, json, time, uuid, random, base64, struct, requests
from modules.crypto_aes import aes_encrypt, aes_decrypt
import numpy as np
import cv2
from typing import Optional
import requests


request_headers = {
    "user-agent": "Dart/2.17 (dart:io)",
    "content-type": "application/json; charset=utf-8",
    "accept-encoding": "gzip",
    "host": "api.moguding.net:9000",
}

login_url = "https://api.moguding.net:9000/session/user/v6/login"
captcha_url = "https://api.moguding.net:9000/session/captcha/v1/get"
check_slider_url = "https://api.moguding.net:9000/session/captcha/v1/check"


def _post_request(url, headers, data, error_message):
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise ValueError(f"{error_message}: {response.text}")
    return response.json()


def get_token(user):
    data = {
        "phone": aes_encrypt(user["phone"]),
        "password": aes_encrypt(user["password"]),
        "captcha": pass_captcha(),
        "loginType": "android",
        "uuid": str(uuid.uuid4()).replace("-", ""),
        "device": "android",
        "version": "5.15.0",
        "t": aes_encrypt(str(int(time.time() * 1000))),
    }
    rsp = _post_request(
        login_url,
        request_headers,
        data,
        "登陆失败, 看到这条提示代表官方接口又更新了, 请在github留issue。",
    )
    user_info = json.loads(aes_decrypt(rsp.get("data", "")))
    # ❗开发环境输出, 打印登录响应内容, 从此查看是否获取到token
    # print(user_info)

    return user_info


def pass_captcha(max_attempts: Optional[int] = 5) -> str:
    """
    通过行为验证码（验证码类型为blockPuzzle）
    """
    attempts = 0
    while attempts < max_attempts:
        time.sleep(random.uniform(0.5, 0.7))
        request_data = {
            "clientUid": str(uuid.uuid4()).replace("-", ""),
            "captchaType": "blockPuzzle",
        }
        captcha_info = _post_request(
            captcha_url, request_headers, request_data, "获取验证码失败"
        )
        slider_data = recognize_captcha(
            captcha_info["data"]["jigsawImageBase64"],
            captcha_info["data"]["originalImageBase64"],
        )
        check_slider_data = {
            "pointJson": aes_encrypt(
                slider_data, captcha_info["data"]["secretKey"], "b64"
            ),
            "token": captcha_info["data"]["token"],
            "captchaType": "blockPuzzle",
        }
        check_result = _post_request(
            check_slider_url, request_headers, check_slider_data, "验证验证码失败"
        )
        if check_result.get("code") != 6111:
            return aes_encrypt(
                captcha_info["data"]["token"] + "---" + slider_data,
                captcha_info["data"]["secretKey"],
                "b64",
            )
        attempts += 1
    raise Exception("验证码验证失败超过最大尝试次数")


def recognize_captcha(target: str, background: str) -> str:
    """识别图像验证码。

    :param target: 目标图像的二进制数据的base64编码
    :type target: str
    :param background: 背景图像的二进制数据的base64编码
    :type background: str

    :return: 滑块需要滑动的距离
    :rtype: str
    """
    target_bytes = base64.b64decode(target)
    background_bytes = base64.b64decode(background)
    res = slide_match(target_bytes=target_bytes, background_bytes=background_bytes)
    target_width = extract_png_width(target_bytes)
    slider_distance = calculate_precise_slider_distance(res[0], res[1], target_width)
    slider_data = {"x": slider_distance, "y": 5}
    return json.dumps(slider_data, separators=(",", ":"))


def slide_match(target_bytes: bytes = None, background_bytes: bytes = None) -> list:
    """获取验证区域坐标

    使用目标检测算法

    :param target_bytes: 滑块图片二进制数据
    :type target_bytes: bytes
    :param background_bytes: 背景图片二进制数据
    :type background_bytes: bytes

    :return: 目标区域左边界坐标, 右边界坐标
    :rtype: list
    """
    target = cv2.imdecode(np.frombuffer(target_bytes, np.uint8), cv2.IMREAD_ANYCOLOR)

    background = cv2.imdecode(
        np.frombuffer(background_bytes, np.uint8), cv2.IMREAD_ANYCOLOR
    )

    background = cv2.Canny(background, 100, 200)
    target = cv2.Canny(target, 100, 200)

    background = cv2.cvtColor(background, cv2.COLOR_GRAY2RGB)
    target = cv2.cvtColor(target, cv2.COLOR_GRAY2RGB)

    res = cv2.matchTemplate(background, target, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    h, w = target.shape[:2]
    bottom_right = (max_loc[0] + w, max_loc[1] + h)
    return [int(max_loc[0]), int(bottom_right[0])]


def extract_png_width(png_binary):
    """从PNG二进制数据中提取图像宽度。

    该函数从给定的PNG格式二进制数据中提取并返回图像的宽度。

    :param png_binary: PNG图像的二进制数据。
    :type png_binary: bytes

    :return: PNG图像的宽度（以像素为单位）。
    :rtype: int

    :raises ValueError: 如果输入数据不是有效的PNG图像, 抛出包含详细错误信息的异常。
    """
    if png_binary[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("无效的PNG签名：不是有效的PNG图像")
    try:
        width = struct.unpack(">I", png_binary[16:20])[0]
    except struct.error:
        raise ValueError("无法从PNG数据中提取宽度信息")

    return width


def calculate_precise_slider_distance(
    target_start_x: int, target_end_x: int, slider_width: int
) -> float:
    """
    计算滑块需要移动的精确距离, 并添加微小随机偏移。

    :param target_start_x: 目标区域的起始x坐标
    :type: int
    :param target_end_x: 目标区域的结束x坐标
    :type: int
    :param slider_width: 滑块的宽度
    :type: int

    :return: 精确到小数点后14位的滑动距离, 包含微小随机偏移
    :rtype: float
    """
    target_center_x = (target_start_x + target_end_x) / 2
    slider_initial_center_x = slider_width / 2
    precise_distance = target_center_x - slider_initial_center_x
    random_offset = random.uniform(-0.1, 0.1)
    final_distance = round(precise_distance + random_offset, 1)

    return final_distance
