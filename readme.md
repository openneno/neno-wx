neno-wx是是使用python编写的用于通过微信订阅号记录笔记到neno的项目。

## 服务器部署

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

必需：公众号的`appid`、公众号的令牌`token`、公众号的消息加解密密钥`encoding_aes_key`、公众号的开发者密码`AppSecret`

如果你希望为其他使用neno的用户提供服务，可以设置redis相关的参数，用于存储其他用户的github Token、Repo，userName。参数包括：redis 地址`redisHost`，redis端口`redisPort`、redis密码`redisPassword`

如果你希望这个订阅号的记录笔记功能只有你才能使用，你需要设置一些环境变量。

包括：github令牌`githubToken`、存储笔记的仓库`githubRepo`、github用户名`githubUserName`、你在订阅号里的用户id加`myselfUserId`。myselfUserId可以在部署完成后，在订阅号里发送`我的用户id`来获取，获取后再设置用户变量`myselfUserId`，重新启动项目即可。



#### 4.启动项目

端口号为9000，有需要可以在main.py中修改。

```sh
python3 -u main.py
```

#### 4.配置端口映射

由于配置微信订阅号的要求，需要将端口号映射到80或者443端口上。





### 腾讯云serverless部署

对于服务器不太了解可以使用此部署方式，此方式也是完全免费的。

#### 1. 登录[腾讯云serverless控制台](https://console.cloud.tencent.com/scf)

#### 2. 新建一个[函数服务](https://console.cloud.tencent.com/scf/list-create)

点击新建，选择<mark>**从头开始**</mark>创建， 函数类型选择<mark>**Web函数**</mark>，     运行环境选择<mark>**Python3.7**</mark>，函数代码选择<mark>**本地上传zip包**</mark>，

neno使用如何微信快速记录笔记

正如[flomo浮墨笔记](https://flomoapp.com/)那样，你可以向订阅号发送笔记进行快速记录。

这里的订阅号可以是你自己的个人订阅号，也可以使用我的订阅号进行测试。<img title="" src="https://github.com/Mran/neno-extension/raw/master/asset/neno-wx.png" alt="" width="439" data-align="inline">

我想你更关心如何将此项目部署到自己后端。

## 部署方式

1. 自有服务器
   
   










