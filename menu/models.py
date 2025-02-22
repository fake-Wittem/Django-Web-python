from django.db import models
from rest_framework import serializers

from role.models import SysRole


# Create your models here.

# 系统菜单类
class SysMenu(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name='菜单名称')
    icon = models.CharField(max_length=100, unique=True, verbose_name='菜单图标')
    parent_id = models.IntegerField(null=True, verbose_name='父菜单ID')
    order_num = models.IntegerField(null=True, verbose_name='菜单顺序')
    path = models.CharField(max_length=200, null=True, verbose_name='路由地址')
    component = models.CharField(max_length=255, null=True, verbose_name='组件路径')
    menu_type = models.CharField(max_length=10, null=True, verbose_name='菜单类型（dir目录 menu菜单 button按钮）')
    perms = models.CharField(max_length=100, null=True, verbose_name='权限标识')
    create_time = models.DateTimeField(null=True, verbose_name='创建时间')
    update_time = models.DateTimeField(null=True, verbose_name='更新时间')
    remark = models.CharField(max_length=500, null=True, verbose_name='备注')

    # 调用sorted时按菜单顺序进行排序
    def __lt__(self, other):
        return self.order_num < other.order_num

    class Meta:
        db_table = 'sys_menu'


# 序列化模型数据，用于返回给前端。需添加子菜单元素
class SysMenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        if hasattr(obj, 'children'):
            serializer_menu_list: list[SysMenuSerializer2] = list()
            for sys_menu in obj.children:
                serializer_menu_list.append(SysMenuSerializer2(sys_menu).data)
            return serializer_menu_list

    class Meta:
        model = SysMenu
        fields = '__all__'


# 序列化模型数据
class SysMenuSerializer2(serializers.ModelSerializer):
    class Meta:
        model = SysMenu
        fields = '__all__'


# 系统角色菜单关联类
class SysRoleMenu(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.PROTECT)
    menu = models.ForeignKey(SysMenu, on_delete=models.PROTECT)

    class Meta:
        db_table = 'sys_role_menu'


# 序列化模型数据，用于返回给前端
class SysRoleMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysRoleMenu
        fields = '__all__'
