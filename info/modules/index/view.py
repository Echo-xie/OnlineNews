"""
    首页路由
date: 18-11-8 下午8:24
"""
import logging
from flask import render_template, current_app
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

from . import index_blu

class MyForm(Form):
    user = StringField('username', validators=[DataRequired()])

# 定义路由函数
@index_blu.route("/")
def index():
    """
        路由函数
    :return:
    """
    logging.debug("调试日志")
    form = MyForm()
    return render_template("news/index.html", form=form)


# 定义路由函数 -- 必定是此路由, 请求网站小图标
@index_blu.route('/favicon.ico')
def favicon():
    # 返回静态文件小图标 -- app上下文发送静态文件
    return current_app.send_static_file('news/favicon.ico')
