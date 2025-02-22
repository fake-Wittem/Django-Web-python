import json
from datetime import datetime

from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework_jwt.settings import api_settings

from menu.models import SysMenu, SysMenuSerializer
from role.models import SysRole, SysUserRole
from user.models import SysUser, SysUserSerializer


# Create your views here.
class TestView(View):

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token is not None and token != '':
            user_list_obj = SysUser.objects.all()
            # QuerySet内对象类型转换成字典类型
            user_list_dict = user_list_obj.values()
            # 把QuerySet转成列表
            user_list = list(user_list_dict)
            return JsonResponse({'code': 200, 'info': '测试', 'data': user_list})
        else:
            return JsonResponse({'code': 401, 'info': '没有访问权限！'})


# 提供token
class JwtTestView(View):

    def get(self, request):
        user = SysUser.objects.get(username='python222', password='123456')
        # 获取荷载处理（内容）
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # 获取解码处理
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 将用户对象传递进去，获取到该对象的属性值
        payload = jwt_payload_handler(user)
        # 将属性值编码成jwt格式的字符串（生成token）
        token = jwt_encode_handler(payload)
        return JsonResponse({'code': 200, 'token': token})


# 处理登录请求
class LoginView(View):
    # 构造菜单树，带children的
    def build_tree_menu(self, sysMenuList: list[SysMenu]):
        result_menu_list = []
        # 将菜单列表转换为字典，方便查找子菜单
        menu_dict = {menu.id: menu for menu in sysMenuList}
        for menu in sysMenuList:
            # 寻找子菜单
            # 先找到父菜单
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
                result_menu_list.append(menu)
        return result_menu_list

    # 处理POST请求
    def post(self, request):
        username = request.GET.get('username')
        password = request.GET.get('password')

        try:
            user = SysUser.objects.get(username=username, password=password)
            # 获取荷载处理（内容）
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            # 获取解码处理
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            # 根据用户ID获取所有角色，再根据角色ID获取所有菜单权限
            # 查询用户所关联的角色ID与角色名称
            role_sql = f'select id, name from sys_role where id in (select role_id from sys_user_role where user_id = {user.id})'
            role_list = SysRole.objects.raw(role_sql)

            # 获取当前用户所有角色名称，返回给前端
            role_names = [role.name for role in role_list]
            print(role_names)

            role_ids_list = [str(row.id) for row in role_list]
            # 查询角色ID所关联的菜单信息
            menu_sql = f'select * from sys_menu where id in (select distinct menu_id from sys_role_menu where role_id in ({','.join(role_ids_list)})'')'
            menu_list = SysMenu.objects.raw(menu_sql)
            # 按照菜单顺序字段进行排序，模型中重写了lt方法
            sorted_menu_list = sorted(menu_list)
            # 构造菜单树，带children
            tree_menu_list = self.build_tree_menu(sorted_menu_list)
            # 序列化菜单树，返回给前端
            serializer_menu = []
            for tree_menu in tree_menu_list:
                serializer_menu.append(SysMenuSerializer(tree_menu).data)

        except Exception as e:
            print(e)
            return JsonResponse({'code': 500, 'info': '用户名或密码错误'})
        return JsonResponse(
            {'code': 200, 'info': '登录成功', 'token': token, 'user': SysUserSerializer(user).data, 'roles': role_names,
             'menuList': serializer_menu})


# 用户修改个人资料请求
class SaveInfoView(View):

    def post(self, request):
        data = json.loads(request.body)
        if data['id'] == -1:
            # 添加
            user_obj = SysUser(username=data['username'], password=data['password'],
                               email=data['email'], phone_number=data['phone_number'],
                               status=data['status'], remark=data['remark'])
            user_obj.create_time = datetime.now().date()
            user_obj.avatar = 'default.jpg'
            user_obj.password = '123456'
            user_obj.save()

        else:
            # 修改
            # 生成模型对象
            user_obj = SysUser(id=data['id'], username=data['username'],
                               password=data['password'],
                               avatar=data['avatar'], email=data['email'],
                               phone_number=data['phone_number'],
                               login_date=data['login_date'],
                               status=data['status'], create_time=data['create_time'],
                               update_time=data['update_time'],
                               remark=data['remark'])
            # 修改更新日期
            user_obj.update_time = datetime.now().date()
            # 保存数据
            user_obj.save()
        return JsonResponse({'code': 200, 'info': '保存成功'})


# 用户操作类
class ActionView(View):

    def get(self, request):
        """
        根据ID获取用户信息
        :param request:
        :return:
        """
        user_id = request.GET.get('id')
        user_obj = SysUser.objects.get(id=user_id)
        return JsonResponse({'code': 200, 'info': '获取用户成功', 'user': SysUserSerializer(user_obj).data})

    def delete(self, request):
        """
        删除用户（批量）
        :param request:
        :return:
        """
        ids_list = json.loads(request.body)
        # 删除用户角色关联数据
        SysUserRole.objects.filter(user_id__in=ids_list).delete()
        SysUser.objects.filter(id__in=ids_list).delete()
        return JsonResponse({'code': 200, 'info': '删除用户成功'})


# 用户名查重类
class CheckView(View):

    def post(self, request):
        """
        验证用户是否存在
        :param request:
        :return:
        """
        data = json.loads(request.body)
        username = data['username']
        if SysUser.objects.filter(username=username).exists():
            return JsonResponse({'code': 500, 'info': '用户已存在！'})
        else:
            return JsonResponse({'code': 200, 'info': '用户验证通过'})


# 修改用户密码请求
class UpdatePwdView(View):

    def post(self, request):
        data = json.loads(request.body)
        user_id = data['id']
        old_pwd = data['oldPassword']
        new_pwd = data['newPassword']
        user_obj = SysUser.objects.get(id=user_id)
        # 验证密码是否正确
        if user_obj.password == old_pwd:
            # 正确，则修改密码
            user_obj.password = new_pwd
            user_obj.update_time = datetime.now().date()
            user_obj.save()
            return JsonResponse({'code': 200, 'info': '密码修改成功'})
        else:
            return JsonResponse({'code': 500, 'info': '原密码错误！'})


# 重置密码
class PasswordResetView(View):
    def get(self, request):
        user_id = request.GET.get('id')
        user_obj = SysUser.objects.get(id=user_id)
        user_obj.password = '123456'
        user_obj.update_time = datetime.now().date()
        user_obj.save()
        return JsonResponse({'code': 200, 'info': '密码重置成功'})


# 用户状态修改
class StatusView(View):

    def post(self, request):
        data = json.loads(request.body)
        user_id = data['id']
        status = data['status']
        user_obj = SysUser.objects.get(id=user_id)
        user_obj.status = status
        user_obj.update_time = datetime.now().date()
        user_obj.save()
        return JsonResponse({'code': 200, 'info': '状态修改成功'})


# 头像文件上传请求
class AvatarUploadView(View):

    def post(self, request):
        file = request.FILES.get('avatar')
        print('file:', file)
        if not file:
            return
        file_name = file.name
        # 文件后缀
        suffix_name = file_name[file_name.rfind('.'):]
        # 重命名文件，年月日时分秒.后缀
        new_file_name = datetime.now().strftime('%Y%m%d%H%M%S') + suffix_name
        # 文件路径，media目录+userAvatar目录+文件名
        file_path = str(settings.MEDIA_ROOT) + '\\userAvatar\\' + new_file_name
        print('file_path:', file_path)
        try:
            # 将上传的文件分块写入文件路径
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            return JsonResponse({'code': 200, 'info': '头像上传成功', 'title': new_file_name})
        except:
            return JsonResponse({'code': 500, 'info': '头像上传失败！'})


# 头像修改请求
class AvatarUpdateView(View):

    def post(self, request):
        data = json.loads(request.body)
        user_id = data['id']
        avatar = data['avatar']
        user_obj = SysUser.objects.get(id=user_id)
        if not user_obj:
            return JsonResponse({'code': 500, 'info': '用户不存在！'})
        user_obj.avatar = avatar
        user_obj.update_time = datetime.now().date()
        user_obj.save()
        return JsonResponse({'code': 200, 'info': '头像修改成功'})


# 用户列表试图
class UserListView(View):

    def post(self, request):
        data = json.loads(request.body)
        page_num = data['pageNum']  # 当前页
        page_size = data['pageSize']  # 每页大小
        query = data['query']  # 查询参数
        # 模糊查询username匹配项目
        user_list_filter = SysUser.objects.filter(username__icontains=query)

        # 总页数
        total_pages = user_list_filter.count()
        if total_pages <= page_size:
            # 当总数小于等于分页大小时，当前页自动设置为第一页
            page_num = 1
        # 分页处理
        user_list_page = Paginator(user_list_filter, page_size).page(page_num)
        # 转成字典后嵌套进list列表
        user_list = list(user_list_page.object_list.values())
        # 添加每个用户所有的角色信息
        for user in user_list:
            user_id = user['id']
            role_list_obj = SysRole.objects.raw(
                f'select id,name from sys_role where id in (select distinct role_id from sys_user_role where user_id = {user_id})'
            )
            role_list = [{'id': role.id, 'name': role.name} for role in role_list_obj]
            user['roles'] = role_list

        return JsonResponse({'code': 200, 'info': '查询成功', 'userList': user_list, 'total': total_pages})


# 用户角色授权
class GrantRoleView(View):

    def post(self, request):
        data = json.loads(request.body)
        user_id = data['id']
        role_ids = data['roleIds']
        # 先删除用户角色关联表的数据
        SysUserRole.objects.filter(user_id=user_id).delete()
        for role_id in role_ids:
            # 保存新的关联数据
            user_role_obj = SysUserRole(user_id=user_id, role_id=role_id)
            user_role_obj.save()
        return JsonResponse({'code': 200, 'info': '修改角色成功'})
