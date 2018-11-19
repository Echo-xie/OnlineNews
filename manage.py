"""
    项目基本配置与测试 -- 只用作最基本的运行工作
date: 18-11-7 下午7:54
"""
from info import create_app, mysql_db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import models
from info.utils.common import add_test_users

# 创建 app, 选择项目环境：development(开发) / production(上线)
app = create_app("development")
# 使用终端脚本工具启动和管理Flask项目
manager = Manager(app)
# 初始化数据库迁移模块
Migrate(app, mysql_db)
# 给终端脚本工具新增数据迁移的相关命令
manager.add_command("db", MigrateCommand)


@manager.option("-n", "--name", dest="name")
@manager.option("-p", "--password", dest="password")
def createsuperuser(name, password):
    """
        使用命令创建管理员用户
    -- python manage.py createsuperuser -n 用户名 -p 密码
    :param name: 用户名
    :param password: 密码
    :return:
    """
    # 判断参数数据是否存在
    if not all([name, password]):
        print("参数不齐")
        return
    # 实例化用户对象
    from info.models import User
    user = User()
    # 保存数据
    user.mobile = name
    user.nick_name = name
    user.password = password
    user.is_admin = True
    try:
        # 数据库新增
        mysql_db.session.add(user)
        # 事务提交
        mysql_db.session.commit()
        #
        print("创建成功")
    except Exception as e:
        print(e)
        mysql_db.session.rollback()


# 运行项目
if __name__ == '__main__':
    # app.run()
    manager.run()

    # 创建测试用户
    # add_test_users()
