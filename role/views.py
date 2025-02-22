import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View

from role.models import SysRole


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
