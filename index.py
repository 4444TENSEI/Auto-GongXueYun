import sys
# sys.path.insert(0, './packages')
import cv2
from modules.load_config import load_config
from modules.send_sign_in_threading import send_sign_in_threading


<<<<<<< HEAD
=======
# 设置重连次数
requests.adapters.DEFAULT_RETRIES = 5
# 时区
shanghai_tz = timezone(timedelta(hours=8))
gmt_time = datetime.now(shanghai_tz)
现在 = datetime.now(shanghai_tz)
# 检查当前时间是否小于 12 点判断上下班打卡
is_start = now.hour < 12


def save(
    user,
    userId,
    token,
    planId,
    province,
    address,
    signType="START",
    device="Android",
    latitude=None,
    longitude=None,
):
    # 修正 create_sign 函数调用
    text = device + signType + planId + userId + address
    headers = {
        "roleKey": "student",
        "user-agent": header_user_agent(user),
        "sign": create_sign(text),
        "authorization": token,
        "content-type": "application/json; charset=UTF-8",
    }
    data = {
        "country": "中国",
        "address": address,
        "province": province,
        "city": user["city"],
        "area": user["area"],
        "latitude": latitude,
        "description": user["desc"],
        "planId": planId,
        "type": signType,
        "device": device,
        "longitude": longitude,
    }
    url = "https://api.moguding.net:9000/attendence/clock/v2/save"
    res = requests.post(url=url, headers=headers, data=json.dumps(data))

    # 检查响应是否为有效的 JSON 格式
    try:
        response_json = res.json()
    except json.JSONDecodeError:
        print(f"服务器返回了无效的 JSON 响应: {res.text}")
        return False, "服务器返回了无效的 JSON 响应"

    # 检查响应中是否包含 'code' 键
    if "code" not in response_json:
        print(f"服务器响应中没有 'code' 键: {response_json}")
        return False, "服务器响应中没有 'code' 键"

    # 正常处理响应
    return response_json["code"] == 200, response_json["msg"]


# startType = 0 使用保持登录状态签到
# startType = 1 使用登录签到
def start_sign(userId, token, planId, user, startType):
    hourNow = datetime.datetime.now(timezone(timedelta(hours=8))).hour
    if hourNow < 12:
        signType = "START"
    else:
        signType = "END"
    phone = user["phone"]
    print("-------------准备签到--------------")

    latitude = user["latitude"]
    longitude = user["longitude"]
    if user["randomLocation"]:
        latitude = latitude[0 : len(latitude) - 1] + str(random.randint(0, 10))
        longitude = longitude[0 : len(longitude) - 1] + str(random.randint(0, 10))

    signResp, msg = save(
        user,
        userId,
        token,
        planId,
        user["province"],
        user["address"],
        signType=signType,
        latitude=latitude,
        longitude=longitude,
    )
    if signResp:
        print("签到成功")
    else:
        print("签到失败")
        if not startType:
            print("-------------签到完成--------------")
            return True

    ######################################
    # 处理推送信息
    pushSignType = "上班"
    if signType == "END":
        pushSignType = "下班"

    pushSignIsOK = "成功！"
    if not signResp:
        pushSignIsOK = "失败！"

    signStatus = "打卡"

    hourNow = datetime.datetime.now(timezone(timedelta(hours=8))).hour
    if hourNow == 11 or hourNow == 23:
        signStatus = "补签"

    # 推送消息内容构建

    push_to_pushplus(
        phone,
        "工学云" + pushSignType + signStatus + pushSignIsOK,
        "用户: " + phone + ", 工学云" + pushSignType + signStatus + pushSignIsOK,
        user["pushKey"],
    )

    # 消息推送处理完毕
    #####################################

    print("-------------签到完成--------------")


def prepare_sign(users):
    # 初始化打卡成功和失败的数量
    success_count = 0
    fail_count = 0

    # 用来存储推送消息的字典, key为pushKey, value为消息内容
    push_messages = {}

    for user in users:
        if not user["enable"]:
            continue
        userInfo = get_token(user)
        phone = user["phone"]
        remark = user.get("remark", "")  # 从配置文件中读取remark值

        user_info_prefix = f"[{remark}/{phone}]"

        if userInfo["code"] != 200:
            print(f"{user_info_prefix}打卡失败, 错误原因: {userInfo['msg']}")
            fail_count += 1
            continue

        userId = userInfo["data"]["userId"]
        token = userInfo["data"]["token"]
        sign = create_sign(userId + "student")
        planId = get_plan_id(user, token, sign)

        # 使用上海时间判断是上班还是下班
        signType = "START" if is_start else "END"
        print(f"{user_info_prefix}准备{signType}打卡\n")

        signResp, msg = save(
            user,
            userId,
            token,
            planId,
            user["province"],
            user["address"],
            signType=signType,
            latitude=user["latitude"],
            longitude=user["longitude"],
        )

        # 推送消息内容构建
        pushSignType = "上班" if signType == "START" else "下班"
        pushSignIsOK = "成功！" if signResp else "失败！"
        signStatus = "打卡"

        hourNow = gmt_time.hour
        if hourNow == 11 or hourNow == 23:
            signStatus = "补签"

        push_message = (
            f"{user_info_prefix}工学云{pushSignType}{signStatus}{pushSignIsOK}\n"
        )
        push_messages.setdefault(user["pushKey"], []).append(push_message)
        # 判断打卡是否成功并更新计数
        if signResp:
            success_count += 1
        else:
            fail_count += 1

    # 合并同pushKey的消息并推送
    for pushKey, messages in push_messages.items():
        # 找到所有具有相同pushKey的用户
        users_with_same_pushkey = [user for user in users if user["pushKey"] == pushKey]
        title = "工学云打卡通知"
        title += f"[{success_count}/{len(users)}]"
        content = "".join(messages)
        content += f"\n打卡时间: {gmt_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        push_to_pushplus(users_with_same_pushkey, title, content, pushKey)

>>>>>>> f9fe15acbfbd47a364deae7d1676583c3c1fc315

def handler(event, context):
    print(cv2.__file__)
        
    # 加载配置信息
    users = load_config()
    # 传入配置信息, 启动项目
    send_sign_in_threading(users)


<<<<<<< HEAD
# ❗1. 开发环境时解除下方的handler(0, 0)用于启动主程序
# ❗2. Github云函数需要保留这一行
# ❗3. 华为云函数需要注释这一行, 否则会连续运行2次打卡任务
=======
# 开发环境时请解除下方注释, 但是请注意在部署时要注释或移除这行, 因为云函数会自动运行一次handler, 不注释掉会造成连续推送2次
>>>>>>> f9fe15acbfbd47a364deae7d1676583c3c1fc315
handler(0, 0)
