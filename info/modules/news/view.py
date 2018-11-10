"""
    新闻视图
date: 18-11-10 下午9:30
"""
from flask import render_template

from info.models import News
from . import news_blu


@news_blu.route("/<int:news_id>")
def detail(news_id):
    """
        新闻详情
    :return:
    """
    # 根据ID获取数据
    news = News.query.get(news_id)
    data={}
    return render_template("news/detail.html", data=data)