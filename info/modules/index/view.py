"""
    首页路由
date: 18-11-8 下午8:24
"""
import logging
from flask import render_template, current_app, session
from flask_wtf.csrf import generate_csrf

from info import constants
from info.models import User, News, Category
from . import index_blu


# 定义路由函数 -- 首页
@index_blu.route("/")
def index():
    """
        路由函数
    :return:
    """
    """获取用户信息"""
    # 获取当前登陆用户ID
    user_id = session.get("user_id")
    # 用户信息
    user_info = None
    try:
        # 通过user_id获取用户信息
        user = User.query.filter(User.id == user_id).first()
        if user:
            # user信息封装字典
            user_info = user.to_dict()
    except Exception as e:
        # 写日志
        current_app.logger.error(e)
    """获取点击排行"""
    # 新闻信息列表
    news_list = []
    try:
        # 访问数据库 获取新闻点击排序数据, 数量最大值为 constants.CLICK_RANK_MAX_NEWS
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 点击排行列表
    click_news_list = []
    # 循环 -- 三目运算 判断 news_list 是否获取到数据
    for news in news_list if news_list else []:
        # 由于是懒加载, news_list是没有具体的值的, 只有调用获取news时, 才去数据库加载数据, 所有需要转换一次
        click_news_list.append(news.to_basic_dict())
    """获取新闻分类"""
    # 获取所有新闻分类
    categories = Category.query.all()
    # 定义列表保存分类数据
    categories_dicts = []
    # 循环新闻分类
    for (atr_index, category) in enumerate(categories):
        # 拼接内容
        categories_dicts.append(category.to_dict())

    # 设置数据
    data = {
        "user_info": user_info,
        "click_news_list": click_news_list,
        "categories": categories_dicts
    }
    # 返回并携带用户信息
    return render_template("news/index.html", data=data)


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
