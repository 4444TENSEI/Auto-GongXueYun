import json, os

# 配置文件本地路径
config_path = "user.json"
# 环境变量名称
config_sys = "USER"


# 环境变量/本地配置加载器(json格式)
def load_config():
    full_config_path = os.path.join(config_path)
    print(f"\n>>>>>>>>>> 打卡任务启动! <<<<<<<<<<\n")
    config_data = {}
    config_loaded = False
    if os.path.exists(full_config_path):
        try:
            with open(full_config_path, "r", encoding="utf-8") as file:
                config_data = json.load(file)
                config_loaded = True
                print(f">>> 配置文件载入成功: {full_config_path}\n")
                # print("载入的配置文件信息: ", config_data)
        except Exception as e:
            print(f"XXX 配置文件加载失败, 请检查文件是否存在: {full_config_path}\n")
    if not config_loaded:
        env_value = os.environ.get(config_sys)
        if env_value:
            try:
                config_data = json.loads(env_value)
                config_loaded = True
                print(f">>> 环境变量加载成功: {config_sys}\n")
                # print("载入的环境变量配置信息: ", config_data)
            except Exception as e:
                print(
                    f"XXX 环境变量加载失败, 请检查是否设置了环境变量键名为{config_sys}!\n"
                )
    if not config_loaded:
        print(
            f"XXX 未找到配置信息，请检查是否设置了环境变量键名为{config_sys}, 或是本地文件路径{config_path}!\n"
        )
    return config_data
