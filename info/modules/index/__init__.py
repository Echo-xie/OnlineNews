"""
    首页蓝图
date: 18-11-9 上午9:11
"""
from flask import Blueprint

index_blu = Blueprint("index",__name__)

from . import views