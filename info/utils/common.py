"""
    通用工具
date: 18-11-10 下午8:21
"""


def do_index_class(index):
    """
        自定义jinja2过滤器，过滤点击排序html的class
        :param index: 下标
    """
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    else:
        return ""
