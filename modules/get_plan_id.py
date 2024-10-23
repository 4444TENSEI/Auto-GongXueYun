import json, requests

from modules.map_headers import header_user_agent


# 获取planId, 忘了干啥的
def get_plan_id(user, token: str, sign: str):
    url = "https://api.moguding.net:9000/practice/plan/v3/getPlanByStu"
    data = {"state": ""}
    headers2 = {
        "roleKey": "student",
        "authorization": token,
        "sign": sign,
        "content-type": "application/json; charset=UTF-8",
        "user-agent": header_user_agent(user),
    }
    res = requests.post(url=url, data=json.dumps(data), headers=headers2)
    return res.json()["data"][0]["planId"]
