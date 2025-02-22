from django.urls import path

from role.views import RoleListAllView, RoleListView

urlpatterns = [
    path('list_all', RoleListAllView.as_view(), name='role_list_all'),  # 获取所有角色
    path('list', RoleListView.as_view(), name='role_list'),  # 角色列表分页查询
]
