# -*-coding:utf-8 -*-

from django.urls import path, re_path
# from django.contrib import admin
from rbac.views import role, user, menu

urlpatterns = [
    # 角色列表展示 url 并添加别名,写项目时都应该加上别名方法，用以做 a 标签的跳转地址
    re_path(r'^role/list/$', role.role_list,name='role_list'),
    # 添加角色 url 并添加别名,写项目时都应该加上别名方法，用以做 a 标签的跳转地址
    re_path(r'^role/add/$', role.role_add, name='role_add'),
    re_path(r'^role/edit/(?P<id>\d+)/$', role.role_edit, name='role_edit'),
    re_path(r'^role/del/(?P<id>\d+)/$', role.role_del, name='role_del'),
    # 用户列表权限相关 url
    # re_path(r'^user/list/$', user.user_list, name='user_list'),
    # re_path(r'^user/add/$', user.user_add, name='user_add'),
    # re_path(r'^user/edit/(?P<id>\d+)/$', user.user_edit, name='user_edit'),
    # re_path(r'^user/del/(?P<id>\d+)/$', user.user_del, name='user_del'),
    # re_path(r'^user/reset/password(?P<id>\d+)/$', user.user_reset_pwd, name='user_reset_pwd'),

    # 权限分配一级菜单的选择和展示编辑删除 url 路由
    re_path(r'^menu/list/$', menu.menu_list, name='menu_list'),
    re_path(r'^menu/add/$', menu.menu_add, name='menu_add'),
    re_path(r'^menu/edit/(?P<id>\d+)/$', menu.menu_edit, name='menu_edit'),
    re_path(r'^menu/del/(?P<id>\d+)/$', menu.menu_del, name='menu_del'),

    # 权限分配二级菜单增加编辑删除 url 路由
    re_path(r'^second/menu/add/(?P<menu_id>\d+)/$', menu.second_menu_add, name='second_menu_add'),
    re_path(r'^second/menu/edit/(?P<id>\d+)/$', menu.second_menu_edit, name='second_menu_edit'),
    re_path(r'^second/menu/del/(?P<id>\d+)/$', menu.second_menu_del, name='second_menu_del'),

    # 权限分配三级菜单增加编辑删除 url 路由
    re_path(r'^permission/add/(?P<second_menu_id>\d+)/$', menu.permission_add, name='permission_add'),
    re_path(r'^permission/edit/(?P<id>\d+)/$', menu.permission_edit, name='permission_edit'),
    re_path(r'^permission/del/(?P<id>\d+)/$', menu.permission_del, name='permission_del'),
    # 权限批量操作 url
    re_path(r'^multi/permissions/$', menu.multi_permission, name='multi_permission'),
    re_path(r'^multi/permissions/del/(?P<pid>\d+)/$', menu.multi_permission_del, name='multi_permission_del'),
    # 权限分配 URL
    re_path(r'^distribute/permission/$', menu.distribute_permission, name='distribute_permission'),
]