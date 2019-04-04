# from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class Permission(models.Model):
    """
    url 权限表
    """
    pid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name="标题", max_length=32)
    url = models.CharField(verbose_name="含正则的url", max_length=128)
    # is_menu = models.BooleanField(verbose_name="是否可为菜单", default=False)
    # blank=True 表示在 django admin 汇总操作时可以为空，null=True 表示数据库中可为空
    # icon = models.CharField(verbose_name="菜单图标", max_length=32, null=True, blank=True)
    url_alias = models.CharField(verbose_name='url 别名', max_length=32, unique=True)
    ppid = models.ForeignKey(verbose_name="关联的权限",
                             help_text="对于非菜单权限需要选择一个可以成为菜单的权限，用于做默认展开和选中菜单",
                             to='Permission', null=True, blank=True,
                             related_name="parents",  # 防止反向关联出错
                             on_delete=models.CASCADE)
    menu_p = models.ForeignKey(verbose_name='所属菜单',
                               to='Menu',
                               null=True, blank=True,
                               help_text='null表示不是菜单，非null表示二级菜单',
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Role(models.Model):
    """
    角色信息记录表
    """
    rid = models.AutoField(primary_key=True)
    role = models.CharField(verbose_name="角色名", max_length=32)
    desc = models.CharField(verbose_name="描述", max_length=128)
    # 创建于权限表的多对多关系
    role_p = models.ManyToManyField(verbose_name="拥有的所有权限", to="Permission", blank=True)

    def __str__(self):
        return self.role


class UserInfo(models.Model):
    """
    用户信息表
    """
    uid = models.AutoField(primary_key=True)
    username = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)
    email = models.CharField(verbose_name="邮箱", max_length=32)
    # 创建与角色表的多对多关系
    user_role = models.ManyToManyField(verbose_name="拥有的角色",
                                       to=Role, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        """
        加上该方法后 django 在做数据库迁移时，将不在为 userinfo 创相关的表以及表结构，
        此 userinfo 类可以当做父类，可以被其它 Model 类继承
        """
        abstract = True


class Menu(models.Model):
    """
    一级菜单数据表
    """
    title = models.CharField(verbose_name='菜单名称', max_length=32)
    icon = models.CharField(verbose_name="菜单图标", max_length=32)

    def __str__(self):
        return self.title
