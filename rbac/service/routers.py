# -*- coding:utf-8 -*-

import re
from django.urls import URLPattern, URLResolver  # 引入 django 中的 url 类型
from collections import OrderedDict
from django.conf import settings
# django 提供的根据字符串形式导入一个模块方法
from django.utils.module_loading import import_string


def  check_url_exclude(url):
    """
    排除一些特定的 url,通常写在 settings 配置文件中
    :param url:
    :return:
    """
    # exclude_url = [
    #     '/admin/.*',
    #     '/login/'
    # ]
    exclude_url = settings.AUTO_DISCOVER_EXCLUDE
    for regex in exclude_url:
        # 使用正则匹配当前 url 是否进行排除，返回 True 表示排除
        if re.match(regex, url):
            return True


def recursion_urls(pre_namespace, pre_url, urlpatterns, url_ordered_dict):
    """
    用于递归的取 URL
    :param pre_namespace: namespace 前缀，用于拼接应用中 url 设置的别名 name
    :param pre_url: URL 前缀，用于拼接应用中 urls 中设置的 URL
    :param urlpatterns: 路由关系列表
    :param url_ordered_dict: 用于保存递归中获取的所由路由
    :return:
    """
    for item in urlpatterns:  # 循环 urls 模块中 urlpatterns 列表中分配的每一个 url 地址
        # 判断 url 的类型，非路由分发则将路由添加到 url_ordered_dict 字典中
        if isinstance(item, URLPattern):
            if not item.name:  # 判断每一个 url 是否设置了 name 别名，如没有则继续循环
                continue

            if pre_namespace:  # 判断根路由分发中是否有设置 namespace 属性,有则进行拼接
                name = "%s:%s" %(pre_namespace, item.name)  # 进行 namespace 与 name 的拼接
            else:
                name = item.name
            # url = pre_url + item._regex  django1.0 版本方法直接替换掉下面一行即可
            url = pre_url + item.pattern.regex.pattern  # 拼接后带符号的路径 /^abc/user/edit/$
            url = url.replace('^', '').replace('$', '') # 去除符号的路径 /abc/user/edit
            if check_url_exclude(url):
                continue
                # 此处 url_alias 原为 name，若有错误可需改回
            url_ordered_dict[name] = {'url_alias':name, 'url':url}
        elif isinstance(item, URLResolver):  # 判断路由类，是路由分发则进行递归操作
            # 如果二级路由中依然有做路由分发而且依然设置了 namespace 到其它路由控制器
            # 中则再次进行 namespace 拼接
            if pre_namespace:
                if item.namespace:  # 如果二级 url 中设置了 namespace 则进行拼接
                    namespace = "%s:%s" %(pre_namespace, item.namespace)
                else:  # 没有则直接使用父级的 namespace
                    namespace = item.namespace
            else:
                if item.namespace:  # 判断如果上级 url 中没有 namespace 则用自己的 namespace
                    namespace = item.namespace
                else:  # 如果一级和二级 url 路由分发中都没有设置 namespace 则直接等于 None
                    namespace = None
            recursion_urls(namespace, pre_url + item.pattern.regex.pattern,
                           item.url_patterns, url_ordered_dict)
            # django 1.0 版本，用下面注释掉的代码替换掉上面一行内容即可
            # recursion_urls(namespace, pre_url + item.regex.pattern,
            #                item.url_patterns, url_ordered_dict)


def get_all_url_dict():
    """
    获取项目中所有 url  (前提必须有 name 别名),
    在其它模块调用该函数则直接可以获取到所有的 url
    :return:
    """
    url_ordered_dict = OrderedDict()
    """
    希望在有序字典中的数据格式:
    {'namespace:name':{name:'namespace:name', url:'xxx/xxx/menu/list'}}
    """
    # 类似导入项目目录中主 urls 路由分配文件模块,并赋值给 md
    md = import_string(settings.ROOT_URLCONF)
    # 调用递归取 url 函数并传参，第一个参数为 None 表示根url没有前缀，
    #   第二个参数 / 表示给每一个根 url 添加一个 / 前缀，
    #   第三个参数即为根目录中 urlpatterns 路由控制中的每个 url，
    #   第四个参数即为使用 OrderedDict 实例华得到的有序字段，用来存放获取到的所有 url
    recursion_urls(None, '/', md.urlpatterns, url_ordered_dict)
    return url_ordered_dict
