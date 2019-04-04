
from django.conf import settings


def init_permission(user_obj, request):
    """
    用户权限信息初始化
    :param user_obj: 当前用户对象
    :param request: request 请求相关所有数据
    :return:
    """
    # 根据当前用户信息获取用户所拥有的所有权限，并放入 session
    # 一：获取当前用户的所有权限
    permission_queryset = user_obj.user_role.filter(role_p__isnull=False) \
        .values('role_p__pk',
                'role_p__title',
                'role_p__url',
                'role_p__url_alias',
                'role_p__ppid_id',
                'role_p__ppid__title',
                'role_p__ppid__url',
                'role_p__menu_p_id',
                'role_p__menu_p__title',
                'role_p__menu_p__icon',
                ).distinct()
    # 二：根据用户分配的权限获取相应权限+菜单信息,将获取到
    #     的所有权限(即url)和菜单信息分别存入字典，并以 url
    #     的别名为 key 方便做权限控制到按钮级别(即在显示按钮
    #     时加上 if 判断进行按钮的显示或不显示)
    permission_dict = dict()
    menu_dict = dict()
    for item in permission_queryset:

        permission_dict[item['role_p__url_alias']] ={
                            'id':item['role_p__pk'],
                            'title':item['role_p__title'],
                            'url':item['role_p__url'],
                            'pid':item['role_p__ppid_id'],
                            'p_title':item['role_p__ppid__title'],
                            'p_url':item['role_p__ppid__url'],
                            }
        menu_id = item['role_p__menu_p_id']
        # 登录成功后从取出来的数据中先判断某一个 url 是否可为菜单，若为空则再次循环
        if not menu_id:
            continue
        # 登录成功后判断菜单 id 是否在 menu_dict 一级菜单字典中，
        # 存在则给当前一级菜单添加二级菜单数据不存在则添加一级菜单和二级菜单
        node = {  # 定义二级菜单数据格式
                'id':item['role_p__pk'],
                'title':item['role_p__title'],
                'url':item['role_p__url']
                }
        if menu_id in menu_dict:
            menu_dict[menu_id]['children'].append(node)
        else:
            menu_dict[menu_id] = {
                'title':item['role_p__menu_p__title'],
                'icon':item['role_p__menu_p__icon'],
                'children':[node, ]
            }
    # 三：将权限及菜单信息保存至 session 中
    request.session[settings.PERMISSION_SESSION_KEY] = permission_dict
    request.session[settings.MENU_SESSION_KEY] = menu_dict


"""
一级菜单用代码只需将下面代码替换掉上面一 二步代码即可使用：
    permission_queryset = user_obj.user_role.filter(role_p__isnull=False) \
                                        .values('role_p__pk',
                                                'role_p__title',
                                                'role_p__is_menu',
                                                'role_p__icon'
                                                'role_p__url').distinct()
        menu_list = list()  一级菜单用列表
        for item in permission_queryset:
            permission_list.append(item['role_p__url'])
            if item['role_p__is_menu']:  # 判断某一项权限(url)是否为菜单
                temp = {
                    'title':item['role_p__title'],
                    'icon':item['role_p__icon'],
                    'url':item['role_p__url']
                }
                menu_list.append(temp)
"""
