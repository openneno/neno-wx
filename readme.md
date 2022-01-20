neno-wx是是使用python编写的用于通过微信订阅号记录笔记到neno的项目。

项目的部署分为两部分

1. 微信订公众号配置
2. 后端服务部署，根据自己的情况选择服务器部署或者是腾讯云serverless部署

## 服务器部署

自有域名和服务器可以选择此方式。

**python版本：3.6**

#### 1.拉取项目

```sh
git clone https://github.com/Mran/neno-wx.git
```

#### 2.安装依赖

```sh
cd neno-wx
pip3 install -r requirements.txt -t .
```

#### 3.修改main.py中的配置参数

必需：公众号的开发者ID`appid`、公众号的开发者密码`AppSecret`、公众号的令牌`token`、公众号的消息加解密密钥`encoding_aes_key`。这些参数在参照下面 微信公众号配置 的内容可以获得。

如果你希望为其他使用neno的用户提供服务，可以设置redis相关的参数，用于存储其他用户的github Token、Repo，userName。参数包括：redis 地址`redisHost`，redis端口`redisPort`、redis密码`redisPassword`

如果你希望这个订阅号的记录笔记功能只有你才能使用，你需要设置一些环境变量。

包括：github令牌`githubToken`、存储笔记的仓库`githubRepo`、github用户名`githubUserName`、你在订阅号里的用户id加`myselfUserId`。myselfUserId可以在部署完成后，在订阅号里发送`我的用户id`来获取，获取后再设置用户变量`myselfUserId`，重新启动项目即可。

#### 4.启动项目

端口号为9000，有需要可以在main.py中修改。

```sh
python3 -u main.py
```

#### 5.配置端口映射

由于配置微信订阅号的要求，需要将端口号映射到80或者443端口上。

## 腾讯云serverless部署

对于服务器不太了解可以使用此部署方式，此方式也是完全免费的。

#### 0.下载代码包

下载项目中的`neno-wx-serverless.zip`，代码包包含了运行 所需要到一些库和启动命令。对serverless部署熟悉的也可以使用编辑代码的方式进行配置。

1. 登录[腾讯云serverless控制台](https://console.cloud.tencent.com/scf)
2. 新建一个[函数服务](https://console.cloud.tencent.com/scf/list-create)
   1. 点击新建，选择**从头开始**创建，
   2. 基础配置里的函数类型选择**Web函数**，运行环境选择**Python3.7**
   3. 函数代码里选择**本地上传zip**，上传`neno-wx-serverless.zip`
   4. 打开高级配置，内存**218MB**，执行超时时间填写**20**秒，环境变量的填写同服务器部署的一致。
   5. 最后点击完成。稍等即可建立函数服务。

3.在触发管理页面里找到访问路径,复制下来。

<br/>

## 微信公众号配置

在公众号的基本配置页面可以找到公众号开发信息,公众号的开发者ID`appid`、公众号的开发者密码`AppSecret`。

服务器配置

1. 填写服务器地址(URL)
2. 如果你是自有域名，例如:你的域名为 `www.neno.com`,那么填写`http://www.neno.com/neno-wx`,配置了https就填写`https://www.neno.com/neno-wx`
3. 如果你是在腾讯云的serverless部署进行的部署,例如:访问路径为`https://service-1234.gz.apigw.tencentcs.com/release/` 那就填写`https://service-qk5a9134-1234.gz.apigw.tencentcs.com/release/neno-wx`
4. 填写令牌(Token)
5. 填写消息加解密密钥(EncodingAESKey),使用自动生成功能即可

  token和消息加解密密钥(EncodingAESKey)都是需要填写到环境变量当中的。

4. 消息加解密方式选择安全模式
5. 点击提交，提示提交成功，即可在你的公众号中发消息进行测试。

## neno使用如何微信快速记录笔记

发送 `我的用户id`可以获得你在这个公众号中的id，主要用于配置仅自己可用时获得自己的用户id

输入 token[你的token] 如token[nenOhVi3pIJn] 配置你的github token

输入 repo[你的笔记仓库名] 如repo[nenonote] 进行配置仓库名称

输入 username[你的github用户名] 如username[mran] 进行配置github用户名

当然这些在使用时都会有提示。

你可以使用我的订阅号进行测试。![](https://github.com/Mran/neno-extension/raw/master/asset/neno-wx.png)
