"""
    首页路由
date: 18-11-8 下午8:24
"""
import logging
from flask import render_template, current_app, session
from flask_wtf.csrf import generate_csrf

from info.models import User
from . import index_blu


# 定义路由函数 -- 首页
@index_blu.route("/")
def index():
    """
        路由函数
    :return:
    """
    # 获取当前登陆用户ID
    user_id = session.get("user_id")
    user_info = None
    try:
        # 通过user_id获取用户信息
        user = User.query.filter(User.id == user_id).first()
        # user信息封装字典
        user_info = user.to_dict()
    except Exception as e:
        # 写日志
        current_app.logger.error(e)
    # 返回并携带用户信息
    return render_template("news/index.html", data={"user_info": user_info})


# 定义路由函数 -- 必定是此路由, 请求网站小图标
@index_blu.route('/favicon.ico')
def favicon():
    # 返回静态文件小图标 -- app上下文发送静态文件
    return current_app.send_static_file('news/favicon.ico')


# 定义路由函数 -- 所有请求访问后
@index_blu.after_request
def after_request(response):
    """
        请求访问后
    :param response: 响应
    :return: 响应
    """
    # 使用flask_wtf库的方法生成 csrf_token
    csrf_token = generate_csrf()
    # 设置cookie
    response.set_cookie("csrf_token", csrf_token)
    # 返回
    return response
