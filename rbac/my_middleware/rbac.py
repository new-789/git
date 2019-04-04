import re
from django.utils.deprecation import MiddlewareMixin  # 导入中间件父类
from django.shortcuts import render
from django.conf import settings


class RbacMiddleware(MiddlewareMixin):
    """
    自编译中间件，可以在用户发送请求时在中间件完成
    用于用户权限信息的校验,
    注：写完中间件需要将自己写的中间件添加到在 settings 文件中的 middleware 中
    """

    def process_request(self, request):
        """
        process_request 用户请求时触发执行
        1、获取的行前用户请求的 url
        2、获取当前用户在 session 中保存的权限(即 url )
        3、使用正则进行用户权限信息的匹配
        :return:
        """
        current_url = request.path_info  # 获取 url 中地址方法
        # 设置白名单，使其中间件对在白名单中的 url不进行权限校验
        for white_url in settings.WHITE_LIST:
            # 为确保多个 url 无需验证
            if re.match(white_url, current_url):
                return None  # 返回 None 表示不拦截执行到下一个中间件或后面的 url

        # 获取 session 保存的权限(即url)
        permission_url_dict = request.session.get(settings.PERMISSION_SESSION_KEY)
        if not permission_url_dict:
            # 未获取到用户权限信息错误及登录页面
            return render(request, 'rbac/user_permission_info.html')

        url_record = [
            {'title': '首页', 'url': '#'}
        ]

        # 此处代码进行判断(需要登录无需通过权限校验)：如果是 /login/ /logout/ /index/
        for url in settings.NO_PERMISSION_LIST:
            if re.match(url, request.path_info):
                request.per_id = 0
                request.homepage_title = url_record
                return None

        # 用户权限匹配，
        state = False  # state 表示无权访问

        for item in permission_url_dict.values():  # 循环从 session 中取出来的字典数据
            reg = '^%s$' % item['url']
            if re.match(reg, current_url):
                state = True  # 权限匹配成功将状态的变量更改为 True 表示可以正常访问
            # 给 request 请求数据中添加一个 per_id 数据方便在任何应用中获取数据
                request.per_id = item['pid'] or item['id']  # 表示默认选中
                # 判断如果当前id 不是 pid 即表示为主菜单
                if not item['pid']:
                    url_record.extend([
                        {'title': item['title'], 'url': item['url'],
                         'class':'activation'}
                    ])
                else:
                    url_record.extend([
                        {'title': item['p_title'], 'url': item['p_url']},
                        {'title': item['title'], 'url': item['url'],'class':'activation'},
                    ])
                request.homepage_title = url_record
                break
        # not state 等于 False 取反为 true 即没有匹配成功没有更改 state 状态为 true
        if not state:
            return render(request, 'rbac/permission_error.html')
