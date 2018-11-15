"""
    通用工具
date: 18-11-10 下午8:21
"""
import functools

from flask import session, g


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
        user_id = session.get("user_id")
        # 默认为False, 用于判断
        user = False
        # 如果有用户ID
        if user_id:
            # 通过id获取用户信息
            from info.models import User
            user = User.query.get(user_id)
        # 保存用户信息
        g.user = user
        return fn(*args, **kwargs)

    return wrapper


import logging
from qiniu import Auth, put_data

# 需要填写你的 Access Key 和 Secret Key
access_key = 'HgfrJJSt1pHNnTFFCbn3r-fMH2xNq0FOIKuPS4SR'
secret_key = 'pP3R81Ojvkiad5q9P2AZF8a9CD_RjhnhySEkqeum'

# 要上传的空间
bucket_name = 'OnlineNews'


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
