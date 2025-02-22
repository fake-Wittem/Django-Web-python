from django.urls import path

from user.views import TestView, JwtTestView, LoginView, SaveInfoView, UpdatePwdView, AvatarUploadView, \
    AvatarUpdateView, UserListView, ActionView, CheckView

urlpatterns = [
    path('test', TestView.as_view(), name='test'),  # 测试
    path('jwt_test', JwtTestView.as_view(), name='jwt_test'),  # jwt测试
    path('login', LoginView.as_view(), name='login'),  # 登录
    path('save_info', SaveInfoView.as_view(), name='save'),  # 保存用户信息
    path('update_password', UpdatePwdView.as_view(), name='update_pwd'),  # 修改用户密码
    path('upload_avatar', AvatarUploadView.as_view(), name='upload_avatar'),  # 头像文件上传
    path('update_avatar', AvatarUpdateView.as_view(), name='update_avatar'),  # 修改头像
    path('list', UserListView.as_view(), name='user_list'),  # 用户列表分页查询
    path('action', ActionView.as_view(), name='user_action'),  # 用户信息操作
    path('check', CheckView.as_view(), name='user_check'),  # 用户名查重
]
