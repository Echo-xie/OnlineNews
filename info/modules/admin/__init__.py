"""
    后台运维管理蓝图
date: 18-11-16 下午6:50
"""
from flask import Blueprint, g, session, redirect, url_for, request, render_template

#
admin_blu = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blu.before_request
def before_request():
    """
        后台运维管理, 请求访问前钩子
    :return:
    """
    # 获取到当前登录用户的id
    user_id = session.get("user_id")
    # 保存用户信息, 默认为False, 用于判断
    g.user = False
    # 请求访问不是后台运维登陆
    if request.path != "/admin/login":
        # 如果没有用户ID
        if not user_id:
            # 跳转至后台运维登陆页面
            return render_template("admin/login.html", errmsg="请登陆管理员账号")
        # 如果有用户ID
        else:
            # 通过id获取用户信息
            from info.models import User
            user = User.query.get(user_id)
            if not user.is_admin:
                # 跳转至后台运维登陆页面
                return render_template("admin/login.html", errmsg="请登陆管理员账号")
            # 保存用户信息
            g.user = user


from . import views
