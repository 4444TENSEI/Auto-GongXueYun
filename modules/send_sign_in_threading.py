import threading
from modules.msg_pusher import push_to_pushplus
from modules.send_sign_in import send_sign_in, global_sign_results, gmt_time


# 并发签到
def send_sign_in_threading(users):
    threads = []
    for user in users:
        if not user["enable"]:
            continue
        thread = threading.Thread(target=send_sign_in, args=(user, 10))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 统一推送消息
    push_messages = {}
    for result in global_sign_results:
        for user in users:
            if f"[{user.get('remark', '')}/{user['phone']}" in result:
                pushKey = user["pushKey"]
                push_messages.setdefault(pushKey, []).append(result)
                break

    for pushKey, messages in push_messages.items():
        users_with_same_pushkey = [user for user in users if user["pushKey"] == pushKey]
        title = "工学云打卡通知"
        title += f"[{len([m for m in messages if '成功' in m])}/{len(messages)}]"
        content = "".join(messages)
        content += f"\n打卡时间: {gmt_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        try:
            push_to_pushplus(users_with_same_pushkey, title, content, pushKey)
        except Exception as e:
            print(f"推送失败, 错误原因: {str(e)}")
