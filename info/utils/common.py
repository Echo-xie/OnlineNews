"""
    通用工具
date: 18-11-10 下午8:21
"""
import functools
import random
from flask import session, g, jsonify, request
from info import RET


def do_index_class(index):
    """
        自定义jinja2过滤器，过滤点击排序html的class
        :param index: 下标
    """
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    else:
        return ""


def user_login_data(fn):
    """
        用户登陆装饰器
    :param fn: 装饰的函数
    :return:
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        """
            装饰步骤
        :param args:
        :param kwargs:
        :return:
        """
        # 获取到当前登录用户的id
        user_id = session.get("face_user_id")
        # 保存用户信息, 默认为False, 用于判断
        g.user = False
        # 如果有用户ID
        if user_id:
            # 通过id获取用户信息
            from info.models import User
            user = User.query.get(user_id)
            if user:
                g.user = user.to_dict()
        return fn(*args, **kwargs)

    return wrapper


def check_login(fn):
    """
        检测用户是否登陆
    :param fn:
    :return:
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        """
            装饰步骤
        :param args:
        :param kwargs:
        :return:
        """
        # 获取到当前登录用户的id
        user_id = session.get("face_user_id")
        # 如果没有用户ID 以及 请求方式为POST
        if not user_id and request.method == "POST":
            return jsonify(errno=RET.SESSIONERR, errmsg="请先登陆用户")
        return fn(*args, **kwargs)

    return wrapper


import logging
from qiniu import Auth, put_data

# 需要填写你的 Access Key 和 Secret Key
access_key = 'HgfrJJSt1pHNnTFFCbn3r-fMH2xNq0FOIKuPS4SR'
secret_key = 'pP3R81Ojvkiad5q9P2AZF8a9CD_RjhnhySEkqeum'
# 要上传的空间
bucket_name = 'onlinenews'


def storage(data):
    """
        七牛云存储上传文件接口
    :param data: 需要上传的二进制文件
    :return: 文件路径
    """
    if not data:
        return None
    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)
        # 生成上传 Token
        token = q.upload_token(bucket_name)
        # 上传文件( Token, 文件名, 二进制文件 )
        ret, info = put_data(token, None, data)
    except Exception as e:
        logging.error(e)
        raise e
    # 判断状态 和 状态码
    if info and info.status_code != 200:
        raise Exception("上传文件到七牛失败")
    # 返回上传文件的网络路径
    return ret["key"]


def add_test_users():
    """
        添加测试用户
    :return:
    """
    import datetime
    users = []
    now = datetime.datetime.now()
    for num in range(0, 10000):
        try:
            from info.models import User
            from info import mysql_db
            from manage import app
            user = User()
            user.nick_name = "%011d" % num
            user.mobile = "%011d" % num
            user.password_hash = "pbkdf2:sha256:50000$SgZPAbEj$a253b9220b7a916e03bf27119d401c48ff4a1c81d7e00644e0aaf6f3a8c55829"
            user.create_time = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            user.last_login = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            users.append(user)
            print(user.mobile)
        except Exception as e:
            print(e)
    with app.app_context():
        mysql_db.session.add_all(users)
        mysql_db.session.commit()
    print('OK')
