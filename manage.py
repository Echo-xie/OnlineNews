"""
    项目基本配置与测试
date: 18-11-7 下午7:54
"""
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# 实例化Flask框架
app = Flask(__name__)
# 设置配置文件
app.config.from_object(Config)

# 通过SQLAlchemy实例化数据库 -- SQLAlchemy读取配置信息时候数据库
mysql_db = SQLAlchemy(app)
# 实例化Redis连接池
pool_14 = redis.ConnectionPool(host=Config.REDIS_HOST, port=Config.REDIS_PORT, password=Config.REDIS_PASSWORD, db=Config.REDIS_SESSION_DB, decode_responses=True)
# 通过连接池实例化Redis数据库 -- 当需要调用某个具体的数据库才去调用相应的连接池, 减少新建和释放的资源
redis_db = redis.Redis(connection_pool=pool_14)

# 开启csrf的防范机制
CSRFProtect(app)
# 初始化数据库迁移模块
Migrate(app, mysql_db)

# 使用终端脚本工具启动和管理Flask项目
manager = Manager(app)
# 给终端脚本工具新增数据迁移的相关命令
manager.add_command('db', MigrateCommand)


# 定义路由函数
@app.route("/")
def index():
    """
        路由函数
    :return:
    """
    return "hello news!"


# 运行项目
if __name__ == '__main__':
    # app.run()
    manager.run()
