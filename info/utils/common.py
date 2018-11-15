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
