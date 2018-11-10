"""
    此包, 用于存放具体业务逻辑的实现
date: 18-11-8 上午6:54
"""
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from info.constants import REDIS_POOL_SELECT_0

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
    """注册蓝图"""
    # 首页蓝图
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    # 验证/通行证蓝图
    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)
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
