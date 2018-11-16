"""
    用户视图
date: 18-11-13 下午3:53
"""
from flask import request, jsonify, g, current_app, render_template, session

from info import mysql_db, constants
from info.models import User, Category, News
from info.response_code import RET
from info.utils.common import storage, check_login
from . import users_blu


@users_blu.route("/info")
@check_login
def info():
    """
        用户信息
    :return:
    """
    # data = {
    #     "user": g.user.to_dict() if g.user else None
    # }
    # return render_template("users/user_info.html", data=data)
    # 封装功能同上
    return users_render_template("users/user_info.html")


@users_blu.route("/user_base_info", methods=["POST", "GET"])
@check_login
def user_base_info():
    """
        修改个人基本信息
    """
    # 当前登陆用户
    user = g.user
    # 请求方式 == get
    if request.method == "GET":
        # # 封装数据
        # data = {
        #     "user": user.to_dict() if user else None
        # }
        # # 返回
        # return render_template("users/user_base_info.html", data=data)
        # 封装功能同上
        return users_render_template("users/user_base_info.html")
    """post提交数据"""
    # 获取请求体
    data_dict = request.json
    # 个性签名
    signature = data_dict.get("signature")
    # 用户名称
    nick_name = data_dict.get("nick_name")
    # 性别
    gender = data_dict.get("gender")
    # 判断参数是否都有数据
    if not all([nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不齐")
    # 判断参数数据是否正确
    if gender not in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 赋值
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender
    try:
        # 事务提交
        mysql_db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        mysql_db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")
    # 修改session属性
    session["nick_name"] = nick_name
    # 返回
    return jsonify(errno=RET.OK, errmsg="更新成功")


@users_blu.route("/user_pic_info", methods=["GET", "POST"])
@check_login
def user_pic_info():
    """
        用户头像上传页面和功能
    :return:
    """
    # 获取登陆用户
    user = g.user
    if request.method == "GET":
        return users_render_template("users/user_pic_info.html")

    try:
        # 获取请求体 -- 二进制上传文件
        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="读取文件出错")

    try:
        # 上传文件
        url = storage(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
    # 保存用户头像路径
    user.avatar_url = constants.QINIU_DOMIN_PREFIX + url
    try:
        # 事务提交
        mysql_db.session.commit()
    except Exception as e:
        mysql_db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户数据错误")
    # 返回
    return jsonify(errno=RET.OK, errmsg="头像上传成功", avatar_url=constants.QINIU_DOMIN_PREFIX + url)


@users_blu.route("/user_follow", methods=["GET", "POST"])
@check_login
def user_follow():
    """
        我的关注
    :return:
    """
    # 获取登陆用户
    user = g.user
    # 获取当前页码
    page = request.args.get("page", 1)
    # 页码
    current_page = 1
    # 总页数
    total_page = 1
    # 用户关注列表实体
    user_followed_entity = []
    try:
        # 转类型
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    try:
        # 分页查询当前用户关注用户列表
        paginate = user.followed.paginate(page, constants.USER_FOLLOWED_MAX_COUNT, False)
        # 获取用户关注列表数据
        user_followed_entity = paginate.items
        # 当前页码
        current_page = paginate.page
        # 总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
    # 封装返回用户关注列表
    user_follow_list = []
    # 循环实体, 封装
    for user in user_followed_entity:
        # 封装
        user_follow_list.append(user)
    # 返回数据
    data = {
        "follows": user_follow_list,
        "current_page": current_page,
        "total_page": total_page
    }
    # 返回
    return render_template('users/user_follow.html', data=data)


@users_blu.route("/follow", methods=['POST'])
@check_login
# @user_login_data
def follow():
    """
        关注用户
    :return:
    """
    # 获取请求访问中的请求体
    data_dict = request.json
    # 动作 -- 关注 / 取消关注
    action = data_dict.get("action")
    # 被关注者
    followed_id = data_dict.get("followed_id")

    # 判断参数数据是否都存在
    if not all([action, followed_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不齐")

    # 如果 actin不是这2个属性
    if action not in ("follow", "un_follow"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 获取当前用户
    user = User.query.get(g.user.id)
    # 设置参数 -- 被关注用户的信息
    followed = User.query.get(followed_id)
    # 判断具体操作 -- 关注/取消关注
    if action == "follow":
        # 关注
        # followers 是粉丝列表
        # followed.followers.append(user)
        # followed 是关注列表 -- 反向
        user.followed.append(followed)
    else:
        # 取消关注
        # followers 是粉丝列表
        # followed.followers.remove(user)
        # followed 是关注列表 -- 反向
        user.followed.remove(followed)
    try:
        # 事务提交
        mysql_db.session.commit()
    except Exception as e:
        # 写日志
        current_app.logger.error(e)
        # 事务回退
        mysql_db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库保存出错")
    # 成功返回
    return jsonify(errno=RET.OK, errmsg="操作成功")


@users_blu.route("/user_pass_info", methods=["GET", "POST"])
@check_login
def user_pass_info():
    """
        密码修改展示, 和修改密码
    :return:
    """
    # 获取登陆用户
    user = g.user
    # 请求方式 == get
    if request.method == "GET":
        # 返回模板
        return users_render_template("users/user_pass_info.html")
    # 获取请求体
    data_dict = request.json
    # 原密码
    old_password = data_dict.get("old_password")
    # 新密码
    new_password = data_dict.get("new_password")
    # 判断参数是否都有数据
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不齐")
    # 判断原密码是否正确
    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")
    # 保存 密码
    user.password = new_password
    try:
        # 事务提交
        mysql_db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        mysql_db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")
    # 返回
    return jsonify(errno=RET.OK, errmsg="密码修改成成功")


@users_blu.route("/user_collection")
@check_login
def user_collection():
    """
        用户收藏新闻列表
    :return:
    """
    # 获取登陆用户
    user = g.user
    # 获取请求体
    page = request.args.get("page", 1)
    try:
        # 转类型
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        # 默认1
        page = 1
    # 收藏新闻集合实体
    collections = []
    # 当前页码
    current_page = 1
    # 总页数
    total_page = 1
    try:
        # 在用户收藏新闻表中查询数据( 当前页码, 分页数量, 不查询 )
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取具体收藏新闻数据
        collections = paginate.items
        # 获取当前页码
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
    # 封装返回收藏新闻集合
    collection_list = []
    # 循环收藏新闻集合实体
    for news in collections:
        # 封装
        collection_list.append(news.to_dict())
    # 返回数据
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "collections": collection_list
    }
    # 返回
    return render_template("users/user_collection.html", data=data)


@users_blu.route("/user_news_release", methods=["GET", "POST"])
@check_login
def user_news_release():
    """
        新闻发布页面和功能
    :return:
    """
    # 获取登陆用户
    user = g.user
    # 请求方式 == get
    if request.method == "GET":
        # 新闻分类集合实体
        categories = []
        try:
            # 获取所有的分类数据
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
        # 封装返回新闻分类数据
        categories_list = []
        # 循环 新闻分类实体
        for category in categories:
            # 封装 -- 获取字典
            categories_list.append(category.to_dict())

        # 移除`最新`分类 -- 最新只需按照创建时间排序, 没有具体的类别
        categories_list.pop(0)
        # 封装返回数据
        data = {
            "categories": categories_list
        }
        return render_template("users/user_news_release.html", data=data)
    # 标题
    title = request.form.get("title")
    # 来源
    source = "个人发布"
    # 摘要
    digest = request.form.get("digest")
    # 正文内容
    content = request.form.get("content")
    # 图片信息 -- 文件
    index_image = request.files.get("index_image")
    # 分类ID
    category_id = request.form.get("category_id")
    # 判断参数是否都有数据
    if not all([title, source, digest, content, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不齐")
    try:
        # 读取图片二进制数据
        index_image = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        # return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")
    # 实例化保存发布新闻数据
    news = News()
    if index_image:
        try:
            # 上传图片信息
            url = storage(index_image)
            news.index_image_url = constants.QINIU_DOMIN_PREFIX + url
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
    # 设置新闻实体属性
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    news.category_id = category_id
    news.user_id = user.id
    # 1代表待审核状态
    news.status = 1
    try:
        # 添加发布新闻数据
        mysql_db.session.add(news)
        # 事务提交
        mysql_db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        mysql_db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    # 返回
    return jsonify(errno=RET.OK, errmsg="发布成功，等待审核")


@users_blu.route("/user_news_list")
@check_login
def user_news_list():
    """
        新闻列表
    :return:
    """
    # 获取登陆用户
    user = g.user  # type: User
    # 获取请求体
    page = request.args.get("page", 1)
    try:
        # 转类型
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        # 默认1
        page = 1
    # 用户新闻列表集合实体
    news_entitys = []
    # 当前页码
    current_page = 1
    # 总页数
    total_page = 1
    try:
        # 在用户新闻表中查询数据( 当前页码, 分页数量, 不查询 )
        paginate = user.news_list.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取具体用户新闻数据
        news_entitys = paginate.items
        # 获取当前页码
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
    # 封装返回用户新闻列表集合
    news_list = []
    # 循环用户新闻列表集合实体
    for news in news_entitys:
        # 封装
        news_list.append(news.to_dict())
    # 返回数据
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_list
    }
    # 返回
    return render_template("users/user_news_list.html", data=data)


def users_render_template(template):
    """
        用户蓝图模块返回
    :param template:
    :return:
    """
    # 封装数据
    data = {
        "user": g.user.to_dict() if g.user else None
    }

    return render_template(template, data=data)
