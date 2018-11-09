"""
    验证/通行证视图
date: 18-11-9 上午9:18
"""
import logging

from flask import request, current_app, jsonify, make_response

from . import passport_blu
# 生成验证码库
from info.utils.captcha.captcha import captcha
from info import constants
from info.utils.response_code import RET



# 定义路由函数
@passport_blu.route("/image_code")
def image_code():
    """
        获取 图片验证码
    :return: 验证码图片
    """
    # 获取uuid
    code_id = request.args.get("code_id")
    # 生成图片验证码 ( 文件名, 验证码内容, 验证码图片 )
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
        # current_app.logging.error(e)
        logging.error(e)
        # 返回json格式数据 -- 保存失败
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))
    # 根据图片生成响应体
    response = make_response(image)
    # 设置响应头 -- 数据类型
    response.headers["Content-Type"] = "image/jpg"
    # 返回
    return response
