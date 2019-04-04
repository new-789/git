# -*- coding:utf-8 -*-

from collections import OrderedDict
from django.shortcuts import render, HttpResponse, redirect
from django.forms import formset_factory
from django.conf import settings
from django.utils.module_loading import import_string
from rbac.forms.menu import MenuModelForm, SecondMenuModelForm, PermissionModelForm
from rbac.forms.menu import MultiAddPermissionForm, MultiEditPermissionForm
from rbac import models
from rbac.service.original_search_urls import memory_reverse
from rbac.service.routers import get_all_url_dict


def menu_list(request):
    """
    权限分配菜单展示列表视图功能函数
    :param request:
    :return:
    """
    menus_obj = models.Menu.objects.all()  # 查找出 Menu 表中的所有数据
    # 取出浏览器 GET 请求的 mid 值并转换成 int 格式数据类型
    menu_id = request.GET.get('mid')  # 用户选择的一级菜单 id
    second_menu_id = request.GET.get('sid')
    menu_exists = models.Menu.objects.filter(id=menu_id).exists()  # 查找当前一级菜单 id 是否存在
    if not menu_exists:  # 判断当前 id 是否存在,不存在则设置一级菜单id为空，防止用户恶意填写id 号
        menu_id = None
    # 查找当前二级菜单 id 是否存在
    second_menu_exists = models.Permission.objects.filter(ppid=second_menu_id).exists()
    if not second_menu_exists:  # 判断当前 id 是否存在,不存在则设置二级菜单id为空，防止用户恶意填写id 号
        second_menu_id = None

    # 根据上一级菜单 id 查找下一级菜单内容
    if menu_id:  # 根据一级菜单 id 查找二级菜单的内容
        second_menus = models.Permission.objects.filter(menu_p=menu_id)
    else:
        second_menus = list()
    if second_menu_id:  # 根据二级菜单 id 查找三级菜单的内容
        permissions_menus = models.Permission.objects.filter(ppid=second_menu_id)
    else:
        permissions_menus = list()
    return render(request, 'rbac/menu_list.html', {'menus': menus_obj,
                                                   'menu_id': menu_id,
                                                   'second_menus': second_menus,
                                                   'second_menu_id': second_menu_id,
                                                   'permissions': permissions_menus})


def menu_add(request):
    """
    新建菜单视图功能函数
    :param request:
    :return:
    """
    if request.method == "GET":
        form = MenuModelForm()
        return render(request, 'rbac/change.html', {'form': form})
    form = MenuModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        url = memory_reverse(request, 'menu_list')
        return redirect(url)
    return render(request, 'rbac/change.html', {'form': form})


def menu_edit(request, id):
    """
    编辑一级菜单视图功能函数
    :param request:
    :param id: 为当前编辑内容的 id
    :return:
    """
    obj = models.Menu.objects.filter(id=id).first()
    if not obj:
        return render(request, 'rbac/menu_error.html')
    if request.method == 'GET':
        form = MenuModelForm(instance=obj)  # instance= 表示给模板传默认值
        return render(request, 'rbac/change.html', {'form': form})
    form = MenuModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        form.save()
        url = memory_reverse(request, 'menu_list')
        return redirect(url)
    return render(request, 'rbac/change.html', {'form': form})


def menu_del(request, id):
    """
    删除一级菜单视图功能函数
    :param request:
    :param id:  为当前删除内容的 id
    :return:
    """
    # origin_url = reverse('menu_del')
    url = memory_reverse(request, 'menu_list')
    if request.method == "GET":
        return render(request, 'rbac/delete.html', {'cancel': url})
    models.Menu.objects.filter(id=id).delete()  # 对数据库进行删除操作

    return redirect(url)


# 权限分配二级菜单增加修改删除视图函数


def second_menu_add(request, menu_id):
    """
    新增二级菜单
    :param request:
    :param menu_id: 当前二级菜单的一级菜单 id (用于设置默认值)
    :return:
    """
    menu_obj = models.Menu.objects.filter(id=menu_id).first()
    if request.method == "GET":
        # initial 表示传过去的数据为选择框或 input 标签的默认值，
        # 传参格式为字典形式，字典的 key 则为 models 中创建数据库表时定义的字段
        form = SecondMenuModelForm(initial={'menu_p': menu_obj})
        return render(request, 'rbac/change.html', {'form': form})
    form = SecondMenuModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        url = memory_reverse(request, 'menu_list')
        return redirect(url)
    return render(request, 'rbac/change.html', {'form': form})


def second_menu_edit(request, id):
    """
    编辑二级菜单
    :param request:
    :param id: 当前要编辑二级菜单的 id 号
    :return:
    """
    permission_obj = models.Permission.objects.filter(pid=id).first()
    if request.method == "GET":
        form = SecondMenuModelForm(instance=permission_obj)
        return render(request, 'rbac/change.html', {'form': form})
    form = SecondMenuModelForm(data=request.POST, instance=permission_obj)
    if form.is_valid():
        form.save()
        url = memory_reverse(request, 'menu_list')
        return redirect(url)
    return render(request, 'rbac/change.html', {'form': form})


def second_menu_del(request, id):
    """
    删除二级菜单
    :param request:
    :return:
    """
    url = memory_reverse(request, 'menu_list')
    if request.method == "GET":
        return render(request, 'rbac/delete.html', {'cancel': url})
    models.Permission.objects.filter(pid=id).delete()  # 对数据库进行删除操作

    return redirect(url)


# 权限分配三级级菜单增加修改删除视图函数


def permission_add(request, second_menu_id):
    """
    三级菜单增加视图功能函数(即添加权限)
    :param request:
    :return:
    """
    # menu_obj = models.Menu.objects.filter(id=menu_id).first()
    if request.method == "GET":
        form = PermissionModelForm()
        return render(request, 'rbac/change.html', {'form': form})

    # 数据校验相关,校验成功则直接保存到数据库
    form = PermissionModelForm(data=request.POST)
    if form.is_valid():
        # 查询传过来的二级菜单是否存在，不存在则返回错误页面
        second_menu_objects = models.Permission.objects.filter(pid=second_menu_id).first()
        if not second_menu_objects:
            return render(request, 'rbac/menu_error.html')
        # form.instance 中包含了用户提交的所有值
        form.instance.ppid = second_menu_objects
        form.save()
        url = memory_reverse(request, 'menu_list')
        return redirect(url)
    return render(request, 'rbac/change.html', {'form': form})


def permission_edit(request, id):
    """
    编辑权限功能视图函数
    :param request:
    :param id: 要编辑的权限 id
    :return:
    """
    permission_obj = models.Permission.objects.filter(pid=id).first()
    if request.method == "GET":
        form = PermissionModelForm(instance=permission_obj)
        return render(request, 'rbac/change.html', {'form': form})
    form = PermissionModelForm(data=request.POST, instance=permission_obj)
    if form.is_valid():
        form.save()
        url = memory_reverse(request, 'menu_list')
        return redirect(url)
    return render(request, 'rbac/change.html', {'form': form})


def permission_del(request, id):
    """
    删除权限功能视图函数
    :param request:
    :param id: 要删除的权限 id
    :return:
    """
    url = memory_reverse(request, 'menu_list')
    if request.method == "GET":
        return render(request, 'rbac/delete.html', {'cancel': url})
    models.Permission.objects.filter(pid=id).delete()  # 对数据库进行删除操作

    return redirect(url)


def multi_permission(request):
    """
    批量操作权限视图函数
    :param request:
    :return:
    """
    post_type = request.GET.get('type')
    increase_formset_class = formset_factory(MultiAddPermissionForm, extra=0)
    update_formset_class = formset_factory(MultiEditPermissionForm, extra=0)
    increase_formset = None
    update_formset = None
    # 判断请求是否为 POST 请求，且判断提交的数据是否为新增数据提交的内容
    if request.method == 'POST' and post_type == 'increase':
        # 批量添加
        formset = increase_formset_class(data=request.POST)
        if formset.is_valid():
            object_list = []  # 创建空列表用于存放需要增加的数据，用来批量增加
            post_row_list = formset.cleaned_data
            has_error = False  # 定义一个标记变量，用来确认是否有错误信息
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                try:
                    new_obj = models.Permission(**row_dict)
                    new_obj. validate_unique()  # 对数据进行唯一约束检测
                    object_list.append(new_obj)
                except Exception as e:
                    formset.errors[i].update(e)
                    increase_formset = formset
                    has_error = True
            if not has_error:
            # 对数据进行批量增加，好过在循环时一条条增加，增加对数据库操作的负担,
            # batch_size 参数表示每次执行的条数
                models.Permission.objects.bulk_create(object_list, batch_size=100)
        else:
            increase_formset = formset
    # 判断请求是否为 POST 请求，且判断提交的数据是否为更新数据操作
    if request.method == 'POST' and post_type == 'update':
        formset = update_formset_class(request.POST)
        if formset.is_valid():
            post_row_list = formset.cleaned_data
            for i in range(0, formset.total_form_count()):
                row_dict = post_row_list[i]
                permission_id = row_dict.pop('pid')
                try:
                    row_object = models.Permission.objects.filter(pid=permission_id).first()
                    for k, v in row_dict.items():
                        setattr(row_object, k, v)
                    row_object.validate_unique()
                    row_object.save()
                except Exception as e:
                    # print(e)
                    formset.errors[i].update(e)
                    update_formset = formset
        else:
            update_formset = formset

    # 第一步获取项目中所有的 URL,并生成一个集合类型的数据
    all_url_dict = get_all_url_dict()
    router_name_set = set(all_url_dict.keys()) # 创建集合

    # 第二步获取数据库中所有的 url，并生成一个集合类型的数据
    permissions = models.Permission.objects.all().values(
        'pid', 'title', 'url_alias',
        'url', 'menu_p_id', 'ppid_id'
    )
    permission_dict = OrderedDict()  # 创建有序字典
    permission_name_set = set()
    for row in permissions:
        permission_dict[row['url_alias']] = row
        permission_name_set.add(row['url_alias']) # 创建集合，给集合中添加内容语法

    # 循环从数据库中取出的 url ，让其与自动获得的 url 进行对比
    # 如果两者不一样则交给用户选择用那个作为权限分配的内容
    for name, value in permission_dict.items():
        # 根据数据库中的 name 从自动获得 url 中进行取值
        router_row_dict = all_url_dict.get(name)
        if not router_row_dict:  # 不存在则再次循环
            continue
        # 判断数据库中的 url 与自动获得的 url 是否一致
        if  value['url'] != router_row_dict['url']:
            value['url'] = '路由和数据库中的 url 不一致'

    # 第三步：对项目创建的集合与数据库数据创建的两个集合进行比较，
    # 用来确定添加、删除、修改的权限有哪些
    # 3.1:通过集合运算计算出需要增加的权限 URL 别名,并创建 fromset 设定显示内容
    # 判断如果 increase_formset 中没有数据说明此次请求为 get 请求，则使用 form 类生成数据进行渲染
    if not increase_formset:
        increase_name_list = router_name_set - permission_name_set
        increase_formset = increase_formset_class(initial=[  # 列表生成式取得需要增加的数据
                                row_dict for name, row_dict in all_url_dict.items()
                                if name in increase_name_list
                                ])

    # 3.2:通过集合运算计算出需要删除的权限 URL 别名
    delete_name_list = permission_name_set - router_name_set  # 需删除的权限 url
    delete_row_list = [
        row_dict for name, row_dict in permission_dict.items()
        if name in delete_name_list
        ]

    # 3.3:通过集合运算计算出需要更新的权限 URL 别名,并创建编辑的 formset
    if not update_formset:
        update_name_list = permission_name_set & router_name_set  # 求交集需更新的权限 url
        update_formset = update_formset_class(initial=[
            row_dict for name, row_dict in permission_dict.items()
            if name in update_name_list
        ])

    return render(request,
                  'rbac/multi_permissions.html',
                  {'increase_formset': increase_formset,
                   'delete_row_list': delete_row_list,
                   'update_formset': update_formset}
                  )


def multi_permission_del(request, pid):
    """
    批量页面的权限删除功能视图函数
    :param request:
    :param pid:
    :return:
    """
    url = memory_reverse(request, 'multi_permission')
    if request.method == "GET":
        return render(request, 'rbac/delete.html', {'cancel': url})
    models.Permission.objects.filter(pid=pid).delete()  # 对数据库进行删除操作

    return redirect(url)

# 权限分配页面视图函数


def distribute_permission(request):
    """
    权限分配功能视图函数
    需构建的数据格式：
    [{'id':1, 'title': xxx,
        '二级菜单(children)':[{'id':2, 'title':ccc, 'menu_p_id':1,
        '三级菜单(children)'：[{'id':3, 'title':vvv:'ppid_id':2}]
        }]
    }]
    :param request:
    :return:
    """
    user_model_class = import_string(settings.RBAC_USER_MODEL_CLASS)
    # 根据用户选择的用户获取相应的角色
    user_id = request.GET.get('uid')
    user_obj = user_model_class.objects.filter(uid=user_id).first()
    if not user_obj:
        user_id = None
    if user_id:
        # 根据用户表得到的内容获取当前用户所拥有的所有角色
        user_has_roles_list = user_obj.user_role.all()
    else:
        user_has_roles_list = []
    # 字典生成式，并设置字典中的 value 为 None，key 则为 item.rid，用来存放用户 id，
    # 因为在页面中进行判断时字典的速度要大于列表
    user_has_roles_dict = {item.rid:None for item in user_has_roles_list}

    # 根据用户选择的角色获取相应的权限
    role_id = request.GET.get('rid')
    role_object = models.Role.objects.filter(rid=role_id).first()
    if not role_object:
        role_id = None

    # 对提交的内容进行保存
    if request.method == 'POST' and request.POST.get('type') == 'role':
        # 获取面板中所有 input 标签为 checkbox 类型的数据
        role_id_list = request.POST.getlist('roles')
        # 将用户和角色的关系添加到第三张表中(多对多关联表)
        if not user_obj:  # 用户不存在则返回选择用户提示
            return HttpResponse('请选择用户，然后在分配角色')
        # 用户存在则通过设置的多对多关联字段进行内容的更新保存
        user_obj.user_role.set(role_id_list)
    if request.method == 'POST' and request.POST.get('type') == 'permission':
        permission_id_list = request.POST.getlist('permissions')
        if not role_object:
            return HttpResponse('请选择角色，然后再分配权限')
        role_object.role_p.set(permission_id_list)


    # 获取当前用户拥有的所有权限，如果选中了角色则优先显示角色所拥有的权限，
    # 若没有选角色则显示用户所拥有的权限
    if role_object:  # 选择了角色
        user_has_permissions = role_object.role_p.all()
        user_has_permissions_dict = {item.pid: None for item in user_has_permissions}
    elif user_obj:  # 未选择角色，但选择了用户
        user_has_permissions = user_obj.user_role\
            .filter(role_p__pid__isnull=False).values('rid', 'role_p').distinct()
        user_has_permissions_dict = {item['role_p']: None for item in user_has_permissions}
    else:
        user_has_permissions = []
        user_has_permissions_dict = {}


    user_obj = user_model_class.objects.all()
    role_obj = models.Role.objects.all()
    menu_permission_list = []
    # 获取所有的一级菜单
    all_menu_list = models.Menu.objects.all().values('id', 'title')
    all_menu_dict = {}
    for item in all_menu_list:
        item['children'] = []  # 用来存放二级菜单
        all_menu_dict[item['id']] = item

    # 获取所有的二级菜单 menu_p 字段不为空的菜单id 名称及它的上级关联 id，
    # 及为科研做二级菜单的内容
    all_second_menu_list = models.Permission.objects.filter(menu_p__isnull=False)\
                            .values('pid', 'title', 'menu_p_id')
    all_second_menu_dict = {}
    for row in all_second_menu_list:
        row['children'] = []  # 用来存放三级菜单
        all_second_menu_dict[row['pid']] = row
        menu_id = row['menu_p_id']
        all_menu_dict[menu_id]['children'].append(row)

    # 获取所有的三级菜单(不能做菜单的权限,即 menu_id 字段为空的内容),
    # menu_p_id=True 允许为空表示该菜单不能为菜单，即为三级菜单
    all_three_menu_list = models.Permission.objects.filter(menu_p__isnull=True)\
                          .values('pid', 'title', 'ppid_id')
    for row in all_three_menu_list:
        pid = row['ppid_id']
        if not pid:  # 判断 pid 是否存在，不存在则表示不合法不进行处理
            continue
        all_second_menu_dict[pid]['children'].append(row)
    return render(request,
                  'rbac/distribute_permission.html',
                  locals()
                   )