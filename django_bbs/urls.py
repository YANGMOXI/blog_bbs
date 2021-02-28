"""django_bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from django.contrib import admin
from app01 import views

# 暴露后端指定文件夹资源
from django.views.static import serve
from django_bbs import settings

urlpatterns = [
    path('', views.home, name='home'),
    path(r'admin/', admin.site.urls),
    # 注册
    path(r'register/', views.register, name='reg'),
    # 登录
    path(r'login/', views.login, name='login'),
    # 图片验证码相关
    path(r'get_code/', views.get_code, name='gc'),
    # 首页
    path(r'home/', views.home, name='home'),

    # 修改密码
    path(r'set_password/', views.set_password, name='set_pwd'),

    # 退出登录
    path(r'logout/', views.logout, name='logout'),

    # 暴露后端指定文件夹资源
    re_path(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),

    # 点赞点踩
    path(r'up_or_down/', views.up_or_down),
    # 评论
    path(r'comment/', views.comment),

    # 后台管理
    path(r'backend/', views.backend),
    # 添加文章
    path(r'add_article/', views.add_article),
    # 富文本编辑器上传文件
    path(r'upload_img/', views.upload_img),
    # 修改用户头像
    path(r'set/avatar/', views.set_avatar),



    # 个人站点
    re_path(r'^(?P<username>\w+)/$', views.site, name='site'),

    # 侧边栏筛选功能
    # url(r'^(?P<username>\w+)/category/(\d+)/', views.site),  # 文章分类
    # url(r'^(?P<username>\w+)/tag/(\d+)/', views.site),  # 文章标签
    # url(r'^(?P<username>\w+)/archive/(\d+)/', views.site),  # 日期归档
    # 将上述3条合并成一条
    re_path(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/', views.site),  # 日期归档

    # 文章详情
    re_path(r'^(?P<username>\w+)/article/(?P<article_id>.*)/', views.article_detail),  # 日期归档



]
