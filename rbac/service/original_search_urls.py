# -*- voding:utf-8 -*-

from django.shortcuts import reverse
from django.http import QueryDict


def memory_url(request, name, *args, **kwargs):
    """
    生成带有原搜索条件的 URL (替代了模板中的 url)
    :param request:
    :param name: 为模板中传过来反向生成的 url 地址
    :return:
    """
    basic_url = reverse(name, args=args, kwargs=kwargs)  # 反向生成 url
    # 判断当前请求的 url 地址中是否带有参数 not 则表示没有带参数
    if not request.GET:
        return basic_url
    # 实例化得到一个 queryDict 特殊空字典类型(GET 请求的数据类型即为该类型的字典数据)
    queryDict = QueryDict(mutable=True)
    # 获取原搜索条件,并添加到 queryDict 特殊字典中
    queryDict['_filter'] = request.GET.urlencode()  # 相当于 mid=11
    # 打包生成地址参数，结果为 queryDict 字典的 key=从 request,GET.urlencode()
    # 获取到的参数，即为 _filter = mid=11
    search_parameter = queryDict.urlencode()
    # 将 url 与 重新打包后的参数进行拼接并返回,返回的实际数据为 _filter=?mid=11
    url = "%s?%s" %(basic_url, search_parameter)
    return url


def memory_reverse(request, name, *args, **kwargs):
    """
    反向生成 url
        http://127.0.0.1:8000/rbac/menu/list/?_filter=mid%3D2
        1、在 url 中将原来的搜索条件获取，如 _filter 后的值
        2.生成原来的 url，如：/menu/list/
        3、返回原搜索条件 url ，如：/menu/list/?_filter=mid%3D2
    :param request:
    :param name:
    :param args:
    :param kwargs:
    :return:
    """
    url = reverse(name, args=args, kwargs=kwargs)
    origin_params = request.GET.get('_filter')
    if origin_params:
        url = "%s?%s" % (url, origin_params)
    return url



"""
方法说明：
    request.GET.urlencode() : 获取为 GET 请求中 url 地址中的所有参数
    示例：
        如请求地址为：127.0.0.1:8000/rbac/menu/list/?mid=11&u=2&f-1
        request.GET.urlencode() 获取到的参数则为问号之后的参数即：mid=11&u=2&f-1
    QueryDict 方法的使用：
        QueryDict 为浏览器 GET 请求数据的特殊字典数据格式，使用该类可实例化得到
        一个空的特殊字典对象
        该类中的 urlencode() 方法说明：
            使用该方法可直接从 request.GET.urlencode() 获取到的请求参数和
            querydict 指定的 key 进行拼接成新的参数
        示例：
            如请求地址为：127.0.0.1:8000/rbac/menu/list/?mid=11
            需求：要求从请求地址中获取到 ? 之后所带的参数并使用 QueryDict 方法将参数
                 拼接并更改为 127.0.0.1:8000/rbac/menu/list/?_filter=mid11
            实现方法：
                第一步：使用 request.GET.urlencode() 方法获取到请求地址中的参数
                    语法：basic_url = request.GET.urlencode()
                第二步：导入 django 中的 QueryDict 类方法，实例化对象，并进行参数拼接
                    导入类语法:from django.http import QueryDict
                    实例化对象语法：query_dict = QueryDict(mutable=True)
                    将参数添加到实例化得到的空字典并制定 key 为 _filter
                        query_dict['_filter'] = basic_url
                    重新打包为需要的数据格式,得到的结果即为：_filter=mid11
                        search_parameter = query_dict.urlencode()
                    进行路径拼接
                        url = "%s?%s" %(basic_url, search_parameter)
                    结果即为：127.0.0.1:8000/rbac/menu/list/?_filter=mid11
"""