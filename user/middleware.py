"""
自定义中间件，通用token鉴权接口
"""
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError
from rest_framework_jwt.settings import api_settings


class JwtAuthenticationMiddleware(MiddlewareMixin):

    # 请求前处理
    def process_request(self, request):
        # 登录请求不需要token验证
        white_list = ['/user/login']  # 请求白名单
        path = request.path
        if path not in white_list and not path.startswith('/media'):
            # 需要进行token验证
            token = request.META.get('HTTP_AUTHORIZATION')
            print('token:', token)
            try:
                # 解析token工具 函数
                jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
                jwt_decode_handler(token)
            except ExpiredSignatureError:
                return HttpResponse('Token过期，请重新登录！')
            except InvalidTokenError:
                return HttpResponse('Token验证失败！')
            except PyJWTError:
                return HttpResponse('Token验证异常！')
        else:
            # 不需要token验证
            return None
