"""
    项目基本配置与测试 -- 只用作最基本的运行工作
date: 18-11-7 下午7:54
"""
from info import create_app, mysql_db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# 创建 app, 选择项目环境：development(开发) / production(上线)
app = create_app("development")
# 使用终端脚本工具启动和管理Flask项目
manager = Manager(app)
# 初始化数据库迁移模块
Migrate(app, mysql_db)
# 给终端脚本工具新增数据迁移的相关命令
manager.add_command("db", MigrateCommand)


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
