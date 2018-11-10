"""
    验证/通行证视图
date: 18-11-9 上午9:18
"""
import logging
import random
import re

from flask import request, jsonify, make_response, current_app

from info.utils.yuntongxun.sms import CCP
from info.models import User
from . import passport_blu
# 生成验证码库
from info.utils.captcha.captcha import captcha
from info import constants
from info.response_code import RET


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
        from info import redis_db
        # 设置限时数据 (key, 限时时间, value)
        redis_db.setex('ImageCode_' + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
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
        from info import redis_db
        # 数据库获取数据
        real_iamge_code = redis_db.get("ImageCode_" + image_code_id)
        # 如果数据获取成功
        if real_iamge_code:
            # 转码
            real_iamge_code = real_iamge_code.decode()
            # 删除数据库数据
            redis_db.delete("ImageCode_" + image_code_id)
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
    # 判断短信是否发送成功
    if result != 0:
        # 短信发送失败
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")
    try:
        # 保存短信验证码
        redis_db.set("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
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
    # parma_dict = dict(eval(request.data))
    # 手机号码
    mobile = parma_dict.get("mobile")
    # 短信验证码
    sms_code = parma_dict.get("sms_code")
    # 密码
    password = parma_dict.get("password")

    """1. 接收参数并判断参数数据是否正确"""
    """2. 验证手机号码是否正确根据手机号码获取对应真实的短信验证码"""
    """3. 对用户输入的短信验证码进行对比验证是否输入正确"""
    """4. 初始化 user 模型，并设置数据并添加到数据库"""
    """5. 保存当前用户的状态"""
    """6. 返回注册的结果"""
    return jsonify(errno=RET.OK, errmsg="新用户注册成功")
