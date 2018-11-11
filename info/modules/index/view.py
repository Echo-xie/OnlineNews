"""
    首页路由
date: 18-11-8 下午8:24
"""
from flask import render_template, current_app, session, request, jsonify, g
from flask_wtf.csrf import generate_csrf

from info import constants
from info.models import User, News, Category
from info.response_code import RET
from info.utils.common import user_login_data
from . import index_blu


# 定义路由函数 -- 首页
@index_blu.route("/")
@index_blu.route("/index")
@user_login_data
def index():
    """
        路由函数
    :return:
    """
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
        "user_info": g.user.to_dict() if g.user else None,
        "click_news_list": click_news_list,
        "categories": categories_dicts
    }
    # 返回并携带用户信息
    return render_template("news/index.html", data=data)


@index_blu.route("/newslist")
def get_news_list():
    """
        获取指定类型新闻列表
    :return:
    """
    # 获取传入参数
    args_dict = request.args
    # 页码
    page = args_dict.get("page")
    # 每页数量
    per_page = args_dict.get("per_page", constants.HOME_PAGE_MAX_NEWS)
    # 分类ID
    category_id = args_dict.get("cid", '1')
    try:
        # 转型
        page = int(page)
        # 转型
        per_page = int(per_page)
    except Exception as e:
        current_app.looger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数类型错误")
    # 条件
    filters = []
    # 如果分类id不为1，那么添加分类id的过滤
    if category_id != "1":
        # 添加条件
        filters.append(News.category_id == category_id)
    try:
        # 根据条件查询数据库, 按创建时间倒叙, 分页查询, 不报错
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
        # 获取查询出来的数据
        items = paginate.items
        # 获取到总页数
        total_page = paginate.pages
        # 当前页码
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    # 新闻列表
    news_li = []
    # 循环
    for news in items:
        # 封装新闻列表
        news_li.append(news.to_basic_dict())

    # 返回数据
    return jsonify(errno=RET.OK, errmsg="OK", totalPage=total_page, currentPage=current_page, newsList=news_li, cid=category_id)


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
