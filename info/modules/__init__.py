"""
    蓝图模块存放目录
date: 18-11-8 下午8:17
"""
from flask import Blueprint

# 实例化蓝图 ( 蓝图名称, 蓝图所在模块 )
index_blu = Blueprint("index", __name__)

# 加载路由 -- 外部只是使用蓝图, 不是使用具体的路由, 而由蓝图去调用相应的路由
from . import views
