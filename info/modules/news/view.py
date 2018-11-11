"""
    新闻视图
date: 18-11-10 下午9:30
"""
from flask import render_template, current_app, abort, g

from info import mysql_db, constants
from info.models import News
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
    # 返回数据
    data = {
        "click_news_list": click_news_list,
        "user_info": g.user.to_dict() if g.user else None,
        "news": news_detail,
    }
    return render_template("news/detail.html", data=data)
