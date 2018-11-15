"""
    新闻视图
date: 18-11-10 下午9:30
"""
from flask import render_template, current_app, abort, g, request, jsonify

from info import mysql_db, constants
from info.models import News, User, Comment, CommentLike
from info.response_code import RET
from . import news_blu


@news_blu.route("/<int:news_id>")
# @user_login_data
def detail(news_id):
    """
        新闻详情
    :return:
    """
    """获取新闻详情"""
    try:
        # 根据ID获取数据
        news_details = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    # 如果新闻数据为空
    if not news_details:
        # 404
        abort(404)
    # 新闻点击 +1
    news_details.clicks += 1
    try:
        # 提交事务
        mysql_db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

    """右侧点击排行"""
    # 右侧新闻点击排行实体
    right_news_list = None
    try:
        # 获取数据, 点击倒叙, 限制数量constants.CLICK_RANK_MAX_NEWS
        right_news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    # 封装新闻列表
    real_right_news = []
    # 循环获取新闻实体列表
    for right_new in right_news_list if right_news_list else []:
        # 封装
        real_right_news.append(right_new.to_dict())
    """新闻评论"""
    # 新闻评论列表
    comments = []
    try:
        # 获取当前新闻的评论
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
    """评论点赞列表"""
    # 如果当前用户已登录
    if g.user:
        try:
            # 获取所有评论ID
            comment_ids = [comment.id for comment in comments]
            # 如果有评论
            if len(comment_ids) > 0:
                # 获取当前用户对当前所有评论的点赞数据
                comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                         CommentLike.user_id == g.user.id).all()
                # 取出数据中所有的评论ID
                comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)
    # 封装后的新闻评论列表
    comment_list = []
    # 循环 新闻评论 实体模型
    for item in comments if comments else []:
        # 当前评论转换字典类型
        comment_dict = item.to_dict()
        # 默认没有点赞
        comment_dict["is_like"] = False
        # 判断当前评论是否在用户点赞评论列表中
        if g.user and item.id in comment_like_ids:
            # 修改点赞
            comment_dict["is_like"] = True
        # 添加 封装后的新闻评论列表
        comment_list.append(comment_dict)
    """是否收藏/是否关注作者"""
    # 判断是否收藏该新闻，默认值为 false
    is_collected = False
    # 当前登录用户是否关注当前新闻作者
    is_followed = False
    # 用户信息
    user = None
    # 如果当前已登陆用户, 判断当前用户是否收藏此新闻
    if g.user:
        # 用户信息
        user = g.user.to_dict()
        # 如果当前新闻在用户收藏新闻列表中
        if news_details in g.user.collection_news:
            # 设置为已收藏
            is_collected = True
        # 如果当前用户关注作者
        if news_details.user.followers.filter(User.id == g.user.id).count() > 0:
            is_followed = True
    """作者总篇数, 粉丝数"""
    news_count = news_details.user.news_list.count()
    followers_count = news_details.user.followers.count()
    # 返回数据
    data = {
        "news": news_details,
        "click_news_list": real_right_news,
        "comment_list": comment_list,
        "is_collected": is_collected,
        "is_followed": is_followed,
        "user": user,
        "news_count": news_count,
        "followers_count": followers_count,
    }
    return render_template("news/detail.html", data=data)


@news_blu.route("/news_comment", methods=["POST"])
# @user_login_data
def news_comment():
    """
        发表评论
    :return:
    """
    # 获取登陆用户信息
    user = g.user
    # 如果没有登陆
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 获取请求体
    data_dict = request.json
    # 新闻ID
    news_id = data_dict.get("news_id")
    # 评论
    content = data_dict.get("content")
    # 回复评论ID
    parent_id = data_dict.get("parent_id")
    # 判断请求体参数是否都有数据
    if not all([content, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不齐")
    try:
        # 根据新闻ID获取新闻信息
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    # 没有新闻信息
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")
    # 初始化评论模型, 保存数据
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = content
    comment.parent_id = parent_id
    # 添加新闻评论数量
    news.comments_count += 1

    # 保存到数据库
    try:
        mysql_db.session.add(comment)
        mysql_db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存评论数据失败")

    # 返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())


@news_blu.route("/comment_like", methods=["POST"])
# @user_login_data
def comment_like():
    """
        点赞/取消点赞
    :return:
    """
    # 获取登陆用户信息
    user = g.user
    # 如果没有登陆
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 获取请求体
    dict_data = request.json
    # 获取评论ID
    comment_id = dict_data.get("comment_id")
    # 判断请求体参数是否都有数据
    if not all([comment_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不齐")
    try:
        # 查询评论详情
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    # 如果没有评论数据
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论数据不存在")
    # 查询当前评论当前用户点赞数据
    comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=user.id).first()
    # 如果没有数据 -- 可以进行点赞
    if not comment_like:
        # 实例化
        comment_like = CommentLike()
        # 评论ID
        comment_like.comment_id = comment_id
        # 用户ID
        comment_like.user_id = user.id
        # 插入数据库
        mysql_db.session.add(comment_like)
        # 增加点赞条数
        comment.like_count += 1
    else:
        # 删除点赞数据
        mysql_db.session.delete(comment_like)
        # 减小点赞条数
        comment.like_count -= 1
    try:
        # 事务提交
        mysql_db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        mysql_db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="操作失败")
    # 返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_blu.route("/news_collect", methods=['POST'])
# @user_login_data
def news_collect():
    """
        新闻收藏/取消收藏
    :return:
    """
    # 获取当前用户
    user = User.query.get(g.user.id)
    # 如果没有登陆
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 获取参数
    dict_data = request.json
    # 获取新闻ID
    news_id = dict_data.get("news_id")
    # 获取是 -- 收藏/取消收藏
    action = dict_data.get("action")
    # 如果没有新闻ID
    if not all([action, news_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不齐")
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
