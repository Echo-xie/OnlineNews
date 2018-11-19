"""
    验证/通行证视图
date: 18-11-9 上午9:18
"""
from datetime import datetime

import redis
from info import redis_pool, REDIS_POOL_SELECT_0, mysql_db
import random
import re
from flask import request, jsonify, make_response, current_app, session, g
from info.utils.yuntongxun.sms import CCP
from info.models import User
from . import passport_blu
# 生成验证码库
from info.utils.captcha.captcha import captcha
from info import constants
from info.response_code import RET


def get_redis(select=REDIS_POOL_SELECT_0):
    """
        根据select返回相应数据库
    :param select: 数据库key
    :return: 数据库连接
    """
    return redis.StrictRedis(connection_pool=redis_pool[select])


# 定义路由函数
@passport_blu.route("/image_code")
def image_code():
    """
        获取 图形验证码 -- json访问
    :return: 验证码图片
    """
    # 获取uuid
    code_id = request.args.get("code_id")
    # 生成图形验证码 ( 文件名, 验证码内容, 验证码图片 )
    name, text, image = captcha.generate_captcha()
    # 捕获异常
    try:
        # 使用时才导入, 不要放在文件头, 文件头没有上下文环境
        # from info import redis_db
        # 设置限时数据 (key, 限时时间, value)
        # redis_db = redis.StrictRedis(connection_pool=redis_pool["pool_0"])
        get_redis().setex('ImageCode_' + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    # 处理异常
    except Exception as e:
        # 写日志 -- error级别
        current_app.logger.error(e)
        # 返回json格式数据 -- 保存失败
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图形验证码失败'))
    # 根据图片生成响应体
    response = make_response(image)
    # 设置响应头 -- 数据类型
    response.headers["Content-Type"] = "image/jpg"
    # 返回
    return response


# 定义路由函数
@passport_blu.route("/send_sms", methods=["POST"])
def send_sms():
    """
        发送短信
    传入参数: json格式
    mobile: 手机号码
    image_code: 用户输入的验证码
    image_code_id: 图形验证码编号

    流程:
    1. 接收参数并判断参数数据是否正确
    2. 验证手机号码是否正确
    3. 根据传入的图片编码获取对应的真实验证码内容
    4. 对用户输入的验证码进行对比验证是否输入正确
    5. 生成并发送短信, 短信内容保存数据库
    6. 返回响应
    :return: 成功发送短信响应
    """
    # 获取请求体
    parma_dict = request.json
    # parma_dict = dict(eval(request.data))
    # 手机号码
    mobile = parma_dict.get("mobile")
    # 用户输入的验证码
    image_code = parma_dict.get("image_code")
    # 图形验证码编号
    image_code_id = parma_dict.get("image_code_id")

    """1. 接收参数并判断参数数据是否正确"""
    # 如果不是全参数都有数据
    if not all([mobile, image_code, image_code_id]):
        # 参数不齐
        return jsonify(errno=RET.PARAMERR, errmsg="参数不齐")
    """2. 验证手机号码是否正确"""
    # 如果手机号码不符合匹配规则
    if not re.match("^1[356789][\d]{9}", mobile):
        # 手机号码不正确
        return jsonify(errno=RET.DATAERR, errmsg="手机号码不正确")
    # 校验该手机是否已经注册
    try:
        # 查询用户表是否存在此手机号码
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        # 数据库查询错误
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if user:
        # 该手机已被注册
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机已被注册")
    """3. 根据传入的图片编码获取对应的真实验证码内容"""
    # 根据图形验证码编号获取数据库中真实的验证码内容
    try:
        # 数据库获取数据
        real_iamge_code = get_redis().get("ImageCode_" + image_code_id)
        # 如果数据获取成功
        if real_iamge_code:
            # 转码
            real_iamge_code = real_iamge_code.decode()
            # 删除数据库数据
            get_redis().delete("ImageCode_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        # 数据库获取数据失败
        return jsonify(errno=RET.DBERR, errmsg="获取图形验证码失败")
    # 判断验证码是否过期
    if not real_iamge_code:
        # 验证码已过期
        return jsonify(errno=RET.NODATA, errmsg="图形验证码已过期")
    """4. 对用户输入的验证码进行对比验证是否输入正确"""
    # 对用户输入的验证码进行比对验证
    if image_code.lower() != real_iamge_code.lower():
        # 验证码输入错误
        return jsonify(errno=RET.DATAERR, errmsg="图形验证码输入错误")
    """5. 生成并发送短信, 短信内容保存数据库"""
    # 生成随机数
    rand_code = random.randint(0, 999999)
    # 获取短信验证码
    sms_code = "%06d" % rand_code
    # 写日志
    current_app.logger.debug("短信验证码为: %s" % sms_code)
    # 发送短信 ( 手机号码, [短信内容, 失效时间-分钟], 模板ID )
    result = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SMS_CODE_TEMPLATE_ID)
    # result = 0
    # 判断短信是否发送成功
    if result != 0:
        # 短信发送失败
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    try:
        # 保存短信验证码
        get_redis().set("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        # 保存短信验证码失败
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")
    """6. 返回响应"""
    return jsonify(errno=RET.OK, errmsg="短信验证码发送成功")


# 定义路由函数
@passport_blu.route("/register", methods=["POST"])
def register():
    """
        新用户注册功能
    传入参数: json格式
    mobile: 手机号码
    smscode: 短信验证码
    password: 密码

    流程:
    1. 接收参数并判断参数数据是否正确
    2. 验证手机号码是否正确根据手机号码获取对应真实的短信验证码
    3. 对用户输入的短信验证码进行对比验证是否输入正确
    4. 初始化 user 模型，并设置数据并添加到数据库
    5. 保存当前用户的状态
    6. 返回注册的结果
    :return:
    """
    # 获取请求体
    parma_dict = request.json
    # 手机号码
    mobile = parma_dict.get("mobile")
    # 短信验证码
    sms_code = parma_dict.get("sms_code")
    # 密码
    password = parma_dict.get("password")

    """1. 接收参数并判断参数数据是否正确"""
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.DATAERR, errmsg="参数不齐")
    """2. 验证手机号码是否正确根据手机号码获取对应真实的短信验证码"""
    # 如果手机号码不符合匹配规则
    if not re.match("^1[356789][\d]{9}", mobile):
        # 手机号码不正确
        return jsonify(errno=RET.DATAERR, errmsg="手机号码不正确")
    # 校验该手机是否已经注册
    try:
        # 查询用户表是否存在此手机号码
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        # 数据库查询错误
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if user:
        # 该手机已被注册
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机已被注册")
    """3. 对用户输入的短信验证码进行对比验证是否输入正确"""
    try:
        # 获取数据库真实短信验证码
        real_sms_code = get_redis().get("SMS_" + mobile)
        # 如果获取 成功
        if real_sms_code:
            real_sms_code = real_sms_code.decode()
    except Exception as e:
        # 获取数据库失败, 写日志
        current_app.logger.error(e)
        # 返回错误信息
        return jsonify(errno=RET.DBERR, errmsg="获取短信验证码失败")
    # 如果真实短信验证码不存在
    if not real_sms_code:
        # 返回过期信息
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码过期")
    # 对比验证用户输入短信验证码是否输入正确
    if sms_code != real_sms_code:
        # 返回输入错误信息
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码输入错误")
    """4. 初始化 user 模型，并设置数据并添加到数据库"""
    user = User(mobile=mobile, nick_name="手机用户:" + mobile, password=password)
    try:
        # 插入数据库
        mysql_db.session.add(user)
        # 事务提交
        mysql_db.session.commit()
    except Exception as e:
        # 数据库错误, 写日志
        current_app.logger.error(e)
        # 事务回滚
        mysql_db.session.rollback()
        # 返回错误信息
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")
    """5. 保存当前用户的状态"""
    # 用户ID
    session["face_user_id"] = user.id
    """6. 返回注册的结果"""
    return jsonify(errno=RET.OK, errmsg="新用户注册成功")


@passport_blu.route("/login", methods=["POST"])
def login():
    """
        用户登陆
    :return:
    """
    # 获取用户提交的数据
    data_dict = request.json
    # 获取手机号码
    mobile = data_dict.get("mobile")
    # 获取密码
    password = data_dict.get("password")
    # 验证传入的数据是否有值
    if not all([mobile, password]):
        # 返回参数不齐信息
        return jsonify(errno=RET.DATAERR, errmsg="参数不齐")
    try:
        # 查询数据库是否有此手机号码的用户
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        # 写日志
        current_app.logger.error(e)
        # 返回查询数据失败信息
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    # 查询成功, 但是无用户数据
    if not user:
        # 返回用户不存在信息
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")
    # 如果密码错误
    if not user.check_passowrd(password):
        # 返回密码错误信息
        return jsonify(errno=RET.PARAMERR, errmsg="密码错误")
    # 登陆成功, 设置用户信息
    # 用户ID
    session["face_user_id"] = user.id
    # 更新用户最后一次登陆时间
    user.last_login = datetime.now()
    try:
        # 事务提交
        mysql_db.session.commit()
    except Exception as e:
        # 写日志
        current_app.logger.error(e)
        # 事务回滚
        mysql_db.session.rollback()
    return jsonify(errno=RET.OK, errmsg="登陆成功")


# 定义路由函数 -- 登出
@passport_blu.route("/logout", methods=["POST"])
def logout():
    """
        用户登出
    :return:
    """
    # 移除 user_id
    session.pop('face_user_id', None)
    # 移除全局g对象中的user信息 -- 如果全局g对象有user属性
    g.user = False
    # 返回
    return jsonify(error=RET.OK, errmsg="ok")
