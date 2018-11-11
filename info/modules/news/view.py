"""
    新闻视图
date: 18-11-10 下午9:30
"""
from flask import render_template, current_app, abort, g

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
    try:
        # 根据ID获取数据
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    # 如果新闻数据为空
    if not news:
        # 404
        abort(404)
    # 新闻点击 +1
    news.clicks += 1
    # 返回数据
    data = {
        "user_info": g.user.to_dict() if g.user else None,
        "news": news,
    }
    return render_template("news/detail.html", data=data)
