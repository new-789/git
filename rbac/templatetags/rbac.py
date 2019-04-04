from django.template import Library
from django.conf import settings
# from django.shortcuts import reverse
# from django.http import QueryDict  # 导入 QueryDict 特殊字典类语法
from collections import OrderedDict  # 导入字典排序模块
from rbac.service import original_search_urls

register = Library()


# @register.inclusion_tag("rbac/static_menu.html")
# def static_menu(request):
#     """
#     创建一级菜单函数
#     :return:
#     """
#     menu_list = request.session[settings.MENU_SESSION_KEY]
#     return {"menu_list":menu_list}


@register.inclusion_tag("rbac/multi_menu.html")
def multi_menu(request):
    """
    创建二级菜单
    :return:
    """
    menu_dict = request.session[settings.MENU_SESSION_KEY]
    # 给获取到的字典 key 进行排序，以保证菜单顺序不变
    key_list = sorted(menu_dict)

    ordered_dict = OrderedDict()  # 实例化得到一个 ordered_dict 空有序字典
    # 循环列表中一级菜单的内容，并添加一个 class 属性
    for key in key_list:
        val = menu_dict[key]
        val['class'] = 'hide'
        # 循环二级菜单的内容，并与请求的 url 与字典中的内容进行匹配，匹配成功则添加 class 属性
        for per in val['children']:
            if per['id'] == request.per_id:
                per['class'] = 'action'
                val['class'] = ''
        ordered_dict[key] = val
    return {"menu_dict": ordered_dict}


@register.inclusion_tag('rbac/homepage_nav.html')
def homepage_nav(request):
    """
    crm 页面主体导航条
    :param request:
    :return:
    """
    record_list = request.homepage_title
    return {"record_list": record_list}


@register.filter
def has_permission(request, url_alias):
    """
    根据用户的权限显示按钮功能函数
    注：使用 filter 进行装饰的函数最多只能有两个参数
    :param request:
    :return:
    """
    # 取出在权限初始化时存储在 session 中权限信息字典信息
    has_permission = request.session[settings.PERMISSION_SESSION_KEY]
    if url_alias in has_permission:  # 判断传过来的 url_alias 是否在 has_permission 字典中
        return True


@register.simple_tag
def memory_url(request, name, *args, **kwargs):
    """
    生成带有原搜索条件的 URL (替代了模板中的 url)
    :param request:
    :param name: 为模板中传过来反向生成的 url 地址
    :return:
    """
    return original_search_urls.memory_url(request, name, *args, **kwargs)




