"""
    新闻视图
date: 18-11-10 下午9:30
"""
from flask import render_template, current_app, abort, g, request, jsonify

from info import mysql_db, constants
from info.models import News
from info.response_code import RET
from info.utils.common import user_login_data
from . import news_blu


@news_blu.route("/<int:news_id>")
@user_login_data
def detail(news_id):
    """
        新闻详情
    :return:
    """
    """获取新闻详情"""
    try:
        # 根据ID获取数据
        news_detail = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    # 如果新闻数据为空
    if not news_detail:
        # 404
        abort(404)
    # 新闻点击 +1
    news_detail.clicks += 1
    try:
        # 提交事务
        mysql_db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

    """右侧点击排行"""
    # 右侧新闻点击排行实体
    news_list = None
    try:
        # 获取数据, 点击倒叙, 限制数量constants.CLICK_RANK_MAX_NEWS
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    # 封装新闻列表
    click_news_list = []
    # 循环获取新闻实体列表
    for news in news_list if news_list else []:
        # 封装
        click_news_list.append(news.to_basic_dict())
    """新闻评论"""
    """作者信息"""
    """是否收藏"""
    # 判断是否收藏该新闻，默认值为 false
    is_collected = False
    # 如果当前已登陆用户, 判断当前用户是否收藏此新闻
    if hasattr(g, "user"):
        # 如果当前新闻在用户收藏新闻列表中
        if news_detail in g.user.collection_news:
            # 设置为已收藏
            is_collected = True
    # 返回数据
    data = {
        "news": news_detail,
        "click_news_list": click_news_list,
        "is_collected": is_collected,
        "user_info": g.user.to_dict() if g.user else None,
    }
    return render_template("news/detail.html", data=data)


@news_blu.route("/news_collect", methods=['POST'])
@user_login_data
def news_collect():
    """
        新闻收藏/取消收藏
    :return:
    """
    # 获取当前用户
    user = g.user
    # 获取参数
    dict_data = request.json
    # 获取新闻ID
    news_id = dict_data.get("news_id")
    # 获取是 -- 收藏/取消收藏
    action = dict_data.get("action")
    # 如果没有新闻ID
    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 如果 actin不是这2个属性
    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        # 根据当前新闻ID获取数据
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    # 如果新闻不存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")
    # 如果是收藏
    if action == "collect":
        # 用户收藏新闻表 -- 添加数据
        user.collection_news.append(news)
    # 否则
    else:
        # 用户收藏新闻表 -- 删除数据
        user.collection_news.remove(news)
    try:
        # 事务提交
        mysql_db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        mysql_db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败")
    # 返回
    return jsonify(errno=RET.OK, errmsg="操作成功")
