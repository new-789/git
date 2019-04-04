# -*- coding:utf-8 -*-

"""角色管理"""

from django.shortcuts import render, redirect
from django.urls import reverse  # 导入反向生成路径方法
from rbac import models
from rbac.forms.role import RoleModelForm


def role_list(request):
    """
    角色列表管理功能视图函数
    :param request:
    :return:
    """
    role_queryset = models.Role.objects.all()
    return render(request, 'rbac/role_list.html', {'roles': role_queryset})


def role_add(request):
    """
    添加角色功能视图函数
    :param request:
    :return:
    """
    if request.method == "GET":
        form = RoleModelForm()
        return render(request, 'rbac/change.html', {'form':form})
    # ModelForm 获取 request.POST 请求中的数据并提交到后台进行校验
    form = RoleModelForm(data=request.POST)
    # is_valid() 为校验成功后保存的所有数据，此处判断 is_valid 中是否有值，有值成功则保存
    if form .is_valid():
        form.save()  # 直接将数据保存到数据库表中
        # reverse 说明: 从urls路由控制器中指定的别名反向生成路径(url)地址
        return redirect(reverse('role_list'))
    # 判断出错则返回错误信息，form 中保存了正确的内容及错误信息内容，所以直接返货 form 即可
    return render(request, 'rbac/change.html', {'form': form})


def role_edit(request, id):
    """
    角色编辑功能视图函数
    :param request:
    :param id: 当前编辑角色的 id 号
    :return:
    """
    obj = models.Role.objects.filter(rid=id).first()
    if not obj:
        return render(request, 'rbac/role_error.html')
    if request.method == 'GET':
        form = RoleModelForm(instance=obj)  # instance= 表示给模板传默认值
        return render(request, 'rbac/change.html', {'form':form})
    form = RoleModelForm(instance=obj, data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse("role_list"))
    return render(request, 'rbac/change.html', {'form': form})


def role_del(request, id):
    """
    角色删除功能视图函数
    :param request:
    :param id: 当前删除角色的 id 号
    :return:
    """
    origin_url = reverse('role_list')  # 反向生成 url 地址方法
    if request.method == "GET":
        return render(request, 'rbac/delete.html', {'cancel':origin_url})
    models.Role.objects.filter(rid=id).delete()  # 对数据库进行删除操作
    return redirect(origin_url)