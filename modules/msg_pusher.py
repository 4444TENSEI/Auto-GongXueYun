import requests


# 推送消息到PushPlus
def push_to_pushplus(users, title, content, token):
    url = (
        "http://www.pushplus.plus/send?token="
        + token
        + "&title="
        + title
        + "&content="
        + content
        + "&template=html"
    )
    resp = requests.post(url)
    result = resp.json()
    if result["code"] == 200:
        for user in users:
            print(f'√ [{user["remark"]}/{user["phone"]}]消息推送成功！')
    else:
        for user in users:
            print(
                f'× [{user["remark"]}/{user["phone"]}]推送消息提醒失败！原因: {result.get("msg", "未知错误")}'
            )
