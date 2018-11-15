"""
    用户视图
date: 18-11-13 下午3:53
"""
from flask import request, jsonify, g, current_app, render_template, session

from info import mysql_db
from info.models import User
from info.response_code import RET
from . import users_blu


@users_blu.route("/info")
def info():
    """
        用户信息
    :return:
    """
    data = {
        "user": g.user.to_dict() if g.user else None
    }
    return render_template("users/user_info.html", data=data)


@users_blu.route("/user_base_info", methods=["POST", "GET"])
def user_base_info():
    """
        修改个人基本信息
    """
    # 当前登陆用户
    user = g.user
    # 请求方式 == get
    if request.method == "GET":
        # 封装数据
        data = {
            "user": user.to_dict() if user else None
        }
        # 返回
        return render_template("users/user_base_info.html", data=data)
    else:
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
            return jsonify(errno=RET.DBERR, errmsg="数据保存失败")
        # 修改session属性
        session["nick_name"] = nick_name
        # 返回
        return jsonify(errno=RET.OK, errmsg="更新成功")


@users_blu.route("/follow", methods=['POST'])
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
