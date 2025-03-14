from django.http import JsonResponse
from django.views import View

from menu.models import SysMenu, SysMenuSerializer


# Create your views here.
# 查询菜单，树状结构
class TreeListView(View):
    # 构建菜单树
    def build_tree_menu(self, menu_list):
        tree_list = []
        # 将菜单列表转换为字典，方便查找子菜单
        menu_dict = {menu.id: menu for menu in menu_list}
        for menu in menu_list:
            # 寻找子节点
            # 先找到父节点
            parent_menu = menu_dict.get(menu.parent_id)
            if parent_menu:
                # 判断父菜单是否含children属性
                if not hasattr(parent_menu, 'children'):
                    # 给父菜单添加children属性
                    parent_menu.children = []
                # 将子菜单添加到父菜单的 children 列表
                parent_menu.children.append(menu)

            # 判断父菜单，添加到集合
            if menu.parent_id == 0:
                tree_list.append(menu)
        return tree_list

    def get(self, request):
        menu_query_set = SysMenu.objects.order_by('order_num')
        menu_list = self.build_tree_menu(menu_query_set)
        # 需序列化列表元素，元素为SysMenu对象
        serialize_menu_list = []
        for menu in menu_list:
            serialize_menu_list.append(SysMenuSerializer(menu).data)
        return JsonResponse({'code': 200, 'info': '查询成功', 'menuList': serialize_menu_list})
