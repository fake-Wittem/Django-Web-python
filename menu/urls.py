from django.urls import path

from menu.views import TreeListView

urlpatterns = [
    path('list', TreeListView.as_view(), name='tree_list'),  # 查询菜单树
]
