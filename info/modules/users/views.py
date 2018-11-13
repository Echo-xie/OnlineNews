"""
    用户视图
date: 18-11-13 下午3:53
"""
from flask import request, jsonify, g, current_app

from info import mysql_db, user_login_data
from info.models import User
from info.response_code import RET
from . import users_blu


@users_blu.route("/follow", methods=['POST'])
@user_login_data
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
        followed.followers.append(user)
    else:
        # 取消关注
        followed.followers.remove(user)
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
