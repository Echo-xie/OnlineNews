"""
    后台运维管理视图
date: 18-11-16 下午6:51
"""
import time
from datetime import datetime, timedelta

from flask import request, render_template, current_app, session, redirect, url_for, g

from info import constants
from info.models import User
from . import admin_blu


@admin_blu.route("/login", methods=["GET", "POST"])
def login():
    """
        后台运维管理登陆
    :return:
    """
    # 请求方式==GET
    if request.method == "GET":
        return render_template("admin/login.html")
    # 获取表单请求体
    data_dict = request.form
    # 获取用户名
    username = data_dict.get("username")
    # 获取密码
    password = data_dict.get("password")
    # 判断参数数据不为空
    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数不齐")
    try:
        # 根据用户名查询数据库
        user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="数据库查询失败")
    # 判断用户是否存在
    if not user:
        return render_template("admin/login.html", errmsg="用户不存在")
    # 判断用户输入密码是否正确
    if not user.check_passowrd(password):
        return render_template("admin/login.html", errmsg="密码错误")
    # 判断用户是否管理员
    if not user.is_admin:
        return render_template("admin/login.html", errmsg="此用户不是管理员身份")
    # 保存用户ID
    session["user_id"] = user.id
    # 保存用户昵称
    session["nick_name"] = user.nick_name
    # 重定向后台运维管理首页
    return redirect(url_for("admin.index"))


@admin_blu.route("/logout")
def logout():
    # 保存用户ID
    session.pop("user_id", None)
    # 保存用户昵称
    session.pop("nick_name", None)
    # 移除全局g对象中的user信息 -- 如果全局g对象有user属性
    g.user = False
    # 返回
    return render_template("admin/login.html", errmsg="退出成功")


@admin_blu.route("/")
def index():
    """
        后台运维管理首页
    :return:
    """
    # 获取登陆用户信息
    user = g.user
    # 封装返回数据
    data = {
        "user": user
    }
    return render_template("admin/index.html", data=data)


@admin_blu.route("/user_count")
def user_count():
    """
        用户统计
    :return:
    """
    # 总人数
    total_count = 0
    # 月新增总数
    mon_count = 0
    # 日新增总数
    day_count = 0
    # 当前时间
    now_time = time.localtime()
    """总人数/月新增总数/日新增总数"""
    try:
        # 获取当前数据库中非管理员的用户总数
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    try:
        # 获取当前时间 yyyy-mm-01 格式日期
        mon_begin = "%d-%02d-01" % (now_time.tm_year, now_time.tm_mon)
        # 通过字符串, 格式化日期
        mon_begin_data = datetime.strptime(mon_begin, "%Y-%m-%d")
        # 获取当前数据库中 本月新增用户总数
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_data).count()
    except Exception as e:
        current_app.logger.error(e)

    try:
        # 获取当前时间 yyyy-mm-dd 格式日期
        day_begin = '%d-%02d-%02d' % (now_time.tm_year, now_time.tm_mon, now_time.tm_mday)
        # 通过字符串, 格式化日期
        day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
        # 获取当前数据库中 当天新增用户总数
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
    """查询图表信息"""
    # 当天 00:00:00 时间
    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # 近30天日期
    active_date = []
    # 近30天新增用户数
    active_count = []

    # 依次添加数据, 再反转
    # 循环31天
    for i in range(0, 31):
        # 新增用户总数
        count = 0
        # 开始时间 = 当前时间 - i天数 (i=1, 1天前)
        begin_date = now_date - timedelta(days=i)
        # 结束时间 = 当前时间 - i - 1 天数 (i=1, 0天前)
        end_date = now_date - timedelta(days=(i - 1))
        # 添加日期, 格式化开始时间
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        try:
            # 获取数据库中 (非管理员, 创建时间 大于等于 开始时间, 创建时间 小于 结束时间)的用户总数
            # 即 -- 某天中, 新增用户数( 倒序获取 )
            count = User.query.filter(User.is_admin == False, User.create_time >= begin_date, User.create_time < end_date).count()
        except Exception as e:
            current_app.logger.error(e)
        # 添加新增用户总数
        active_count.append(count)
    # 翻转列表
    active_date.reverse()
    # 翻转列表
    active_count.reverse()
    # 封装返回数据
    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_date": active_date,
        "active_count": active_count
    }

    return render_template('admin/user_count.html', data=data)


@admin_blu.route("/user_list")
def user_list():
    """
        用户列表
    :return:
    """
    # 封装返回用户列表
    user_list = []
    # 实体用户列表
    user_enitiy_list = []
    # 获取请求体 -- 页码
    page = request.args.get("page", 1)
    # 当前页码
    current_page = 1
    # 总页数
    total_page = 1

    try:
        # 转类型
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    try:
        # 分页查询( 非管理员, 最后登陆倒序)
        paginate = User.query.filter(User.is_admin == False).order_by(User.last_login.desc()).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        # 当前页码查询数据
        user_enitiy_list = paginate.items
        # 当前页码
        current_page = paginate.page
        # 总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
    # 循环实体用户列表
    for user in user_enitiy_list:
        # 封装
        user_list.append(user.to_dict())
    # 封装返回数据
    data = {
        "user_list": user_list,
        "current_page": current_page,
        "total_page": total_page
    }

    return render_template('admin/user_list.html', data=data)
