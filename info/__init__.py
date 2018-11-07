"""
    此包, 用于存放具体业务逻辑的实现
date: 18-11-8 上午6:54
"""
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

# 实例化MySQL数据库
mysql_db = SQLAlchemy()
# Redis连接池
redis_pool = {}
# Redis数据库
redis_db = None


def create_app(config_name):
    """
        app工厂方法 -- 配置生成app后返回
    :param config_name: 配置文件名称
    :return: app -- Flask实例化
    """
    global mysql_db, redis_db
    # 根据配置文件名称加载配置文件
    config_cls = config[config_name]
    """app实例化配置"""
    # 实例化Flask框架
    app = Flask(__name__)
    # 设置配置文件
    app.config.from_object(config_cls)
    """数据库配置"""
    # 配置数据库 -- 根据app加载的配置信息
    mysql_db.init_app(app)
    # 实例化Redis连接池
    pool_14 = redis.ConnectionPool(host=config_cls.REDIS_HOST, port=config_cls.REDIS_PORT, password=config_cls.REDIS_PASSWORD, db=config_cls.REDIS_SESSION_DB, decode_responses=True)
    # 添加连接池
    redis_pool["pool_14"] = pool_14
    # 通过连接池实例化Redis数据库 -- 当需要调用某个具体的数据库才去调用相应的连接池, 减少新建和释放的资源
    redis_db = redis.Redis(connection_pool=redis_pool["pool_14"])
    """app的额外配置"""
    # 开启csrf的防范机制
    CSRFProtect(app)
    # 设置session保存位置
    Session(app)
    """返回"""
    return app
