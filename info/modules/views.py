"""
    首页路由
date: 18-11-8 下午8:24
"""
import logging
from flask import render_template, current_app
from . import index_blu


# 定义路由函数
@index_blu.route("/")
def index():
    """
        路由函数
    :return:
    """
    logging.debug("调试日志")
    return render_template("news/index.html")

# 定义路由函数 -- 必定是此路由, 请求网站小图标
@index_blu.route('/favicon.ico')
def favicon():
    # 返回静态文件小图标 -- app上下文发送静态文件
    return current_app.send_static_file('news/favicon.ico')

