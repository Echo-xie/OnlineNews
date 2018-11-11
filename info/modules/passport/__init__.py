"""
    验证/通行证蓝图
date: 18-11-9 上午9:17
"""
from flask import Blueprint
# 实例化蓝图, 并设置访问前缀
passport_blu = Blueprint("passport", __name__, url_prefix="/passport")

from . import views
