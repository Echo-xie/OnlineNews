"""
    用户蓝图
date: 18-11-13 下午3:52
"""
from flask import Blueprint
# 实例化蓝图, 并设置访问前缀
users_blu = Blueprint("users", __name__, url_prefix="/users")

from . import views