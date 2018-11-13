"""
    此包, 用于存放具体业务逻辑的实现
date: 18-11-8 上午6:54
"""
import json
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, session, current_app, g, make_response, jsonify, render_template
from config import config
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_session import Session
from info.constants import REDIS_POOL_SELECT_0
from info.utils.common import do_index_class, user_login_data

# 实例化MySQL数据库
mysql_db = SQLAlchemy()
# Redis连接池
redis_pool = {}


def create_app(config_name):
    """
        app工厂方法 -- 配置生成app后返回
    :param config_name: 配置文件名称
    :return: app -- Flask实例化
    """
    # 配置项目日志
    setup_log(config_name)
    # 根据配置文件名称加载配置文件
    config_cls = config[config_name]
    """app实例化配置"""
    # 实例化Flask框架
    app = Flask(__name__)
    # 设置配置文件
    app.config.from_object(config_cls)
    # 添加jinja2过滤器
    app.add_template_filter(do_index_class, "index_class")
    """注册蓝图"""
    # 首页蓝图
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    # 验证/通行证蓝图
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
    # 新闻蓝图
    from info.modules.news import news_blu
    app.register_blueprint(news_blu)
    # 用户蓝图
    from info.modules.users import users_blu
    app.register_blueprint(users_blu)
    """数据库配置"""
    # 配置数据库 -- 根据app加载的配置信息
    mysql_db.init_app(app)
    # 实例化Redis连接池
    pool_0 = redis.ConnectionPool(host=config_cls.REDIS_HOST, port=config_cls.REDIS_PORT, password=config_cls.REDIS_PASSWORD, db=config_cls.REDIS_DATA_DB)
    # 添加连接池
    # 通过连接池实例化Redis数据库 -- 当需要调用某个具体的数据库才去调用相应的连接池, 减少新建和释放的资源
    redis_pool[REDIS_POOL_SELECT_0] = pool_0
    """app的额外配置"""
    # 开启csrf的防范机制
    CSRFProtect(app)
    # 设置session保存位置
    Session(app)

    """定义app路由"""

    @app.errorhandler(404)
    @user_login_data
    def page_not_found(_):
        user = g.user
        data = {"user_info": user.to_dict() if user else None}
        return render_template('news/404.html', data=data)
        return app

    @app.before_request
    def before_request():
        """
            每次请求访问执行前执行
        :return:
        """
        # 获取到当前登录用户的id
        user_id = session.get("user_id")
        #
        user = False
        # 通过id获取用户信息
        if user_id:
            from info.models import User
            user = User.query.get(user_id)
        # 保存用户信息
        g.user = user

    # 定义路由函数 -- 所有请求访问后
    @app.after_request
    def after_request(response):
        """
            请求访问后
        :param response: 响应
        :return: 响应
        """
        # # 获取session中的用户ID
        # user_id = session.get("user_id")
        # # 用户对象
        # user = ""
        # try:
        #     # 根据用户ID查询数据
        #     from info.models import User
        #     user = User.query.get(user_id)
        # except Exception as e:
        #     current_app.logger.error(e)
        #     # abort(404)
        # # 如果用户对象获取成功
        # if user:
        #     # 设置全局用户信息
        #     g.user = user
        #     # 用户信息 -- 字典封装
        #     user_info = user.to_dict()
        #     # 最后返回的数据
        #     real_data = {}
        #     # 如果已有返回数据
        #     if response.get_json():
        #         # 获取原有返回数据
        #         real_data = response.get_json()
        #     # 添加返回数据
        #     real_data['user_info'] = user_info
        #     # 重新封装response响应
        #     response.data = json.dumps(real_data)
        # ( 前后端不分离, 无法实现 )

        # 使用flask_wtf库的方法生成 csrf_token
        csrf_token = generate_csrf()
        # 设置cookie
        response.set_cookie("csrf_token", csrf_token)
        # 返回
        return response

    """返回"""
    return app


def setup_log(config_name):
    """
        配置日志
    :param config_name: 配置文件名
    """

    # 设置日志的记录等级 -- 根据配置文件名称设置不同级别的日志
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    # 实例化日志处理器, 设置(日志保存的路径, 每个日志文件的最大内存, 保存的日志文件个数上限, 编码格式)
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 实例化日志记录的格式 ( 级别 文件名 代码行号 日志信息 )
    formatter = logging.Formatter("%(levelname)s %(filename)s:%(lineno)d %(message)s")
    # 日志处理器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局日志工具对象设置日志处理器
    logging.getLogger().addHandler(file_log_handler)
