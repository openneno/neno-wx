import datetime
import imghdr
import time
from sanic import Sanic
from sanic.response import text
from wechatpy import parse_message
from wechatpy.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException
from wechatpy.replies import create_reply
from wechatpy.utils import check_signature
import redis
import requests
import json
import bson
import re
import base64
import os

app = Sanic("neno-wx")

# 公众号的appid
appid = ""
if len(appid) == 0:
    appid = os.environ.get('appid')

# 公众号的令牌(Token)
token = ""
if len(token) == 0:
    token = os.environ.get('token')

# 公众号的消息加解密密钥
encoding_aes_key = ""
if len(encoding_aes_key) == 0:
    encoding_aes_key = os.environ.get('encoding_aes_key')

# 公众号的开发者密码(AppSecret)
AppSecret = ""
if len(AppSecret) == 0:
    AppSecret = os.environ.get('AppSecret')

# redis 地址
redisHost = ""
if len(redisHost) == 0:
    redisHost = os.environ.get('redisHost')

# redis端口
redisPort = 0
if redisPort == 0:
    redisPort = int(os.environ.get('redisPort'))

# redis密码
redisPassword = ""
if len(redisPassword) == 0:
    redisPassword = os.environ.get('redisPassword')

myselfUserId = os.environ.get('myselfUserId')
if myselfUserId is None:
    r = redis.Redis(host=redisHost, port=redisPort, db=0, password=redisPassword)
crypto = WeChatCrypto(token, encoding_aes_key, appid)


@app.get("/neno-wx")
def nenoWXGET(request):
    print(request.args)
    signature = request.args.get("signature")
    echostr = request.args.get("echostr")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    try:
        check_signature(token, signature, timestamp, nonce)
        return text(echostr)
    except InvalidSignatureException:
        return text("hello")


@app.post("/neno-wx")
def nenoWXPOST(request):
    signature = request.args.get("signature")
    msg_signature = request.args.get("msg_signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")

    from_xml = request.body.decode("UTF-8")
    try:
        check_signature(token, signature, timestamp, nonce)
        try:
            decrypted_xml = crypto.decrypt_message(
                from_xml,
                msg_signature,
                timestamp,
                nonce
            )
        except (InvalidAppIdException, InvalidSignatureException):
            pass
        msg = parse_message(decrypted_xml)
        # print(msg.content)
        userId = msg.source
        if (findExistMag(msg.id) is not None):
            return text("")
        r.set("msgId_{}".format(msg.id), msg.id)
        if msg.type == "text":
            content = msg.content

            if content == "我的用户id":
                return text(ceeateReply(userId, msg, nonce, timestamp))
            if content == "删除我的github配置":
                clearUserGithubSetting(userId)
                return text(ceeateReply("已删除", msg, nonce, timestamp))
            if myselfUserId is not None:
                if myselfUserId == userId:
                    return singleUser(content, "", msg, userId, nonce, timestamp)
                else:
                    return text(ceeateReply("当前只有指定用户才可使用此功能", msg, nonce, timestamp))
            else:
                try:
                    return multipleUser(content, "", msg, userId, nonce, timestamp)

                except BaseException as e:
                    return text(ceeateReply(str(e), msg, nonce, timestamp))
        elif msg.type == "image":
            photo = getFileDown(msg.image)

            if myselfUserId is not None:
                if myselfUserId == userId:
                    return singleUser("微信图片", photo, msg, userId, nonce, timestamp)
                else:
                    return text(ceeateReply("当前只有指定用户才可使用此功能", msg, nonce, timestamp))
            else:
                try:
                    return multipleUser("微信图片", photo, msg, userId, nonce, timestamp)
                except BaseException as e:
                    return text(ceeateReply(str(e), msg, nonce, timestamp))
        else:
            return text(ceeateReply('不支持此类型的数据', msg, nonce, timestamp))
    except InvalidSignatureException:
        return text("hello")


@app.post("/neno-tg")
def nenoTGPOST(request):
    return ()


def singleUser(content, photo, msg, userId, nonce, timestamp):
    githubToken = os.environ.get('githubToken')
    githubRepo = os.environ.get('githubRepo')
    githubUserName = os.environ.get('githubUserName')
    return reply(githubToken, githubRepo, githubUserName, content, photo, msg, nonce, timestamp)


def multipleUser(content, photo, msg, userId, nonce, timestamp):
    if content.startswith("token[") and content.endswith("]"):
        githubToken = content[6:-1]
        r.set("githubToken_{}".format(userId), githubToken)
        return text(ceeateReply('githubToken 已设置', msg, nonce, timestamp))
    elif content.startswith("repo[") and content.endswith("]"):
        repo = content[5:-1]
        r.set("githubRepo_{}".format(userId), repo)
        return text(ceeateReply('github笔记仓库名 已设置', msg, nonce, timestamp))

    elif content.startswith("username[") and content.endswith("]"):
        username = content[9:-1]
        r.set("githubUserName_{}".format(userId), username)
        return text(ceeateReply('github用户名 已设置', msg, nonce, timestamp))

    githubToken, githubRepo, githubUserName = findGithubConfigByUserT(userId)
    if githubToken is None:
        return text(
            ceeateReply('githubToken没有配置\n输入 token[你的token] \n如token[nenOhVi3pIJn] 进行配置', msg, nonce, timestamp))
    elif githubRepo is None:
        return text(ceeateReply('github笔记仓库名没有配置\n输入 repo[你的笔记仓库名] \n如repo[nenonote] 进行配置', msg, nonce, timestamp))

    elif githubUserName is None:
        return text(
            ceeateReply('github用户名没有配置\n输入 username[你的github用户名] \n如username[mran] 进行配置', msg, nonce, timestamp))
    else:
        githubToken = githubToken.decode("UTF-8")
        githubRepo = githubRepo.decode("UTF-8")
        githubUserName = githubUserName.decode("UTF-8")
        return reply(githubToken, githubRepo, githubUserName, content, photo, msg, nonce, timestamp)


def getFileDown(filePath):
    response = requests.request("GET", filePath)
    photoContent = response.content
    return photoContent


def reply(githubToken, githubRepo, githubUserName, content, photo, msg, nonce, timestamp):
    photoId = ""
    suffixName = ""
    if photo != "":
        status_code, retext, photoId, suffixName = sendNenoPhotoToGithub(githubToken, githubRepo, githubUserName, photo)

    status_code, retext = sendNenoContentToGithub(githubToken, githubRepo, githubUserName, content, photoId, suffixName)
    if (status_code == 201):
        return text(ceeateReply('保存成功', msg, nonce, timestamp))
    elif status_code == 401:
        return text(ceeateReply('错误码:{} token错误\n信息:{}'.format(status_code, retext), msg, nonce, timestamp))
    elif status_code == 404:
        return text(ceeateReply('错误码:{} 仓库名或用户名错误\n信息:{}'.format(status_code, retext), msg, nonce, timestamp))
    else:
        return text(ceeateReply('发生未知错误', msg, nonce, timestamp))


# 创建回复到微信的消息
def ceeateReply(replyContent, msg, nonce, timestamp):
    reply = create_reply(replyContent, message=msg)
    xml = reply.render()
    encrypted_xml = crypto.encrypt_message(xml, nonce, timestamp)
    r.delete("msgId_{}".format(msg.id), msg.id)
    return encrypted_xml


def clearUserGithubSetting(userId):
    r.delete("githubToken_{}".format(userId))
    r.delete("githubRepo_{}".format(userId))
    r.delete("githubUserName_{}".format(userId))


# 从redis获得保存的消息id，用于排重
def findExistMag(msgId):
    return r.get("msgId_{}".format(msgId))


# 从redis获得保存的用户github设置
def findGithubConfigByUserT(userId):
    githubToken = r.get("githubToken_{}".format(userId))
    githubRepo = r.get("githubRepo_{}".format(userId))
    githubUserName = r.get("githubUserName_{}".format(userId))
    # print(githubToken, githubRepo, githubUserName)
    return githubToken, githubRepo, githubUserName


# 根据用户的github设置将照片发送到github
def sendNenoPhotoToGithub(githubToken, githubRepo, githubUserName, photo):
    photoId = str(bson.ObjectId())

    suffixName = imghdr.what(None, photo)

    url = "https://api.github.com/repos/{}/{}/contents/picData/{}.{}".format(githubUserName, githubRepo,
                                                                             photoId, suffixName)

    payload = json.dumps({
        "content": base64.b64encode(photo).decode("utf-8"),
        "message": "pic upload wx"
    })
    headers = {
        'authorization': 'token {}'.format(githubToken),
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response.status_code, response.text, photoId)
    return response.status_code, response.text, photoId, suffixName


# 根据用户的github设置将内容发送到github
def sendNenoContentToGithub(githubToken, githubRepo, githubUserName, content, photoId, suffixName):
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    createTime = datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset), microsecond=0).isoformat()
    createDate = createTime[:10]
    _id = str(bson.ObjectId())

    url = "https://api.github.com/repos/{}/{}/contents/{}/{}.json".format(githubUserName, githubRepo, createDate, _id)
    tags = re.findall(r"#\S*", content)
    images = []
    if photoId != "":
        images = [{
            "key": photoId,
            "suffixName": suffixName
        }]
    neno = {
        "content": "<p>{}</p>".format(content),
        "pureContent": content,
        "_id": _id,
        "parentId": "",
        "source": "wechat",
        "tags": tags,
        "images": images,
        "created_at": createTime,
        "sha": "",
        "update_at": createTime
    }
    base64Content = base64.b64encode(json.dumps(neno, sort_keys=True, indent=4, ensure_ascii=False).encode("UTF-8"))
    payload = json.dumps({
        "content": base64Content.decode("UTF-8"),
        "message": "[ADD] {}".format(content)
    })
    headers = {
        'authorization': 'token {}'.format(githubToken),
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    # print(response.text)
    # print(response.status_code)
    return response.status_code, response.text

app.run(host="0.0.0.0", port=9000, debug=False)
