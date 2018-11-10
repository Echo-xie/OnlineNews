"""
    新闻模块蓝图
date: 18-11-10 下午9:29
"""
from flask import Blueprint
# 实例化蓝图, 并设置访问前缀
news_blu = Blueprint("news", __name__, url_prefix="/news")

from . import view