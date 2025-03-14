from django.urls import path

from role.views import RoleListAllView, RoleListView, ActionView, SaveRoleView, MenusView

urlpatterns = [
    path('list_all', RoleListAllView.as_view(), name='role_list_all'),  # 获取所有角色
    path('list', RoleListView.as_view(), name='role_list'),  # 角色列表分页查询
    path('save_role', SaveRoleView.as_view(), name='save_role'),  # 保存角色信息
    path('action', ActionView.as_view(), name='role_action'),  # 角色信息操作
    path('menus', MenusView.as_view(), name='menus'),  # 查询角色拥有的菜单ID
]
