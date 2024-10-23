

### *华为云函数简易部署+微信消息推送，支持多用户同时打卡、消息合并推送，轻量零成本。*

基于下方项目做的合并简化，**只保留了打卡功能**

1. https://github.com/Rockytkg/AutoMoGuDingCheckIn
2. https://github.com/XuanRanDev/Auto-GongXueYun-2

> # ※云函数免费部署: 

> ## 华为云函数（推荐）

1. [下载最新版](https://github.com/4444TENSEI/Auto-GongXueYun/releases/latest)压缩包(.zip)
2. 跟着**图文教程**走：[华为云函数部署Python定时任务](https://blog.yokaze.top/archives/930)
3. 创建云函数导入ZIP源码后，滚动到页面底部，点击左下角**添加依赖包**、搜索: `cryptography_41.0.7_python39`
4. **环境变量键名**为`USER`，参考文档下方配置文件示例，自行修改后复制，在云函数设置中创建**环境变量**

> ## GitHub工作流（有BUG，需要自行测试）

暂时有部分依赖缺失的问题，目前没有时间测试，有心人可以查看项目目录下的**/github/workflows/clock.yml**文件，更改加入缺失的依赖包并自行测试

1. Fork仓库，修改一下本文下方示例中的json配置，复制内容
2. 依次进入克隆后的仓库页面上方的:`Settings`  → `Actions secrets and variables` → `Actions`
3. 点击`New repository secret`，Name输入框填写`USER`，Secret输入框里粘贴刚刚复制的`json配置`，如果要多用户，则复制一次数据体自己改改，然后点击下方绿色`Add secret`按钮保存
4. 回到仓库左上角的`Actions`，点击左侧的`打卡`，点击右侧的`Run workflow`，**再次点击**绿色的Run workflow按钮即可开始定时任务

> # 开发环境/测试

- 安装依赖

```
pip install -r requirements.txt
```

- 运行

```
py index.py
```



> # ※基于提到的项目所做的修改: 

1. 多用户时，打卡推送的消息内容**合并到同一条pushplus消息**，避免了每个用户都会单独推送。

2. 增加了详细的调试语句输出

3. 更新登录/获取token的接口为最新的v6（这里的滑块验证码和AES解密方法大力感谢参考的项目作者[Rockytkg](https://github.com/Rockytkg)，大家可以去帮忙点点star）

4. 简化减少了没必要的配置项，更新了获取token的接口and加解密用的库

5. 新增了配置项: `remark`，作为用户名备注

6. 并发

7. 解耦、模块化

   

   ## 现在的配置文件示例（环境变量键名设置为`USER`）: 

   

   ```
   [
     {
       "remark": "自定义用户名，用于通知中标识用户",
       "phone": "手机号",
       "password": "密码",
       "province": "xx省",
       "city": "xx市",
       "area": "xx区",
       "address": "最终打卡页面显示的文字，xx省 · xx市 · 某路边",
       "longitude": "经度(精确到小数点后六位)",
       "latitude": "纬度(精确到小数点后六位)",
       "randomLocation": true,
       "enable": true,
       "desc": "打卡备注",
       "pushKey": "pushplus官网获取的key，需要实名"
     }
   ]
   ```

### 各项配置含义: 

| 参数名称        | 含义                                                         |
| --------------- | :----------------------------------------------------------- |
| remark          | 自定义用户备注名称                         |
| phone           | 手机号                                                       |
| password        | 密码                                                         |
| randomLocation  | 是否启用打卡位置浮动，启用后每次打卡会在原有位置基础上进行位置浮动 |
| province        | 省份                                                         |
| city            | 城市                                                         |
| area            | 区/县                                                        |
| desc            | 打卡备注                                                     |
| address         | 详细地址，如果你打卡的时候中间带的有·这个符号你也就手动加上，这里填什么，打卡后工学云就会显示你填的内容（工学云默认·这个符号左右都会有一个空格） |
| longitude       | 打卡位置经度,通过坐标拾取来完成(仅需精确到小数点后6位)，[自行查询传送门](https://jingweidu.bmcx.com/) |
| latitude        | 打卡位置纬度,通过坐标拾取来完成(仅需精确到小数点后6位)，[自行查询传送门](https://jingweidu.bmcx.com/) |
| passwordpushKey | 密码打卡结果微信推送，微信推送使用的是pushPlus，请到官网绑定微信([传送门](https://www.pushplus.plus/))，然后在发送消息里面把你的token复制出来粘贴到pushKey这项 |

