import json
from datetime import datetime

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View

from menu.models import SysRoleMenu
from role.models import SysRole, SysRoleSerializer, SysUserRole


# Create your views here.
# 获取所有角色
class RoleListAllView(View):

    def get(self, request):
        role_obj = SysRole.objects.all().values()
        role_list = list(role_obj)
        return JsonResponse({'code': 200, 'roleList': role_list})


# 角色信息查询
class RoleListView(View):

    def post(self, request):
        data = json.loads(request.body)
        page_num = data['pageNum']  # 当前页
        page_size = data['pageSize']  # 每页大小
        query = data['query']  # 查询参数
        # 模糊查询name匹配项目
        role_list_filter = SysRole.objects.filter(name__icontains=query)

        # 总页数
        total_pages = role_list_filter.count()
        if total_pages <= page_size:
            # 当总数小于等于分页大小时，当前页自动设置为第一页
            page_num = 1
        # 分页处理
        role_list_page = Paginator(role_list_filter, page_size).page(page_num)
        # 转成字典后嵌套进list列表
        role_list = list(role_list_page.object_list.values())

        return JsonResponse({'code': 200, 'info': '查询成功', 'roleList': role_list, 'total': total_pages})


# 修改角色请求
class SaveRoleView(View):

    def post(self, request):
        data = json.loads(request.body)

        if data['id'] == -1:
            # 添加
            role_obj = SysRole(name=data['name'], code=data['code'], remark=data['remark'])
            role_obj.create_time = datetime.now().date()
            # 保存数据
            role_obj.save()

        else:
            # 修改
            # 生成模型对象
            role_obj = SysRole(id=data['id'], name=data['name'],
                               code=data['code'], remark=data['remark'])
            # 修改更新日期
            role_obj.update_time = datetime.now().date()
            # 保存数据
            role_obj.save()
        return JsonResponse({'code': 200, 'info': '保存成功'})


# 角色基本操作类
class ActionView(View):

    def get(self, request):
        """
        根据ID获取角色信息
        :param request:
        :return:
        """
        role_id = request.GET.get('id')
        role_obj = SysRole.objects.get(id=role_id)
        return JsonResponse({'code': 200, 'info': '获取角色成功', 'role': SysRoleSerializer(role_obj).data})

    def delete(self, request):
        """
        根据ID删除角色（批量）
        :param request:
        :return:
        """
        ids_list = json.loads(request.body)
        SysUserRole.objects.filter(role_id__in=ids_list).delete()  # 删除用户角色关联表
        SysRoleMenu.objects.filter(role_id__in=ids_list).delete()  # 删除角色菜单关联表
        SysRole.objects.filter(id__in=ids_list).delete()  # 删除角色
        return JsonResponse({'code': 200, 'info': '删除角色成功'})


# 获取角色拥有的菜单权限
class MenusView(View):

    def get(self, request):
        role_id = request.GET.get('id')
        # 获取该角色拥有的菜单字典，key为menu_id，value为菜单ID
        menu_dict = SysRoleMenu.objects.filter(role_id=role_id).values('menu_id')
        menu_id_list = [menu['menu_id'] for menu in menu_dict]
        return JsonResponse({'code': 200, 'info': '查询成功', 'menuIdList': menu_id_list})
