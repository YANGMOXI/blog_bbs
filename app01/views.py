from django.shortcuts import render, HttpResponse, redirect
from app01.myforms import MyRegForm
from app01 import models
from django.http import JsonResponse
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from utils.mypage import Pagination


# Create your views here.


def register(request):
    form_obj = MyRegForm()
    back_dic = {'code': 1000, 'msg': ''}

    if request.method == 'POST':
        form_obj = MyRegForm(request.POST)

        # 判断数据是否合法
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data
            # 将字典中的confirm_password删除
            clean_data.pop('confirm_password')
            print(clean_data)

            # 用户头像
            file_obj = request.FILES.get('avatar')
            if file_obj:
                clean_data['avatar'] = file_obj

            # 操作数据库，保存数据
            models.UserInfo.objects.create_user(**clean_data)
            # 注册成功跳转url
            back_dic['url'] = '/login/'

        # 错误逻辑
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)

    return render(request, 'register.html', locals())


def login(request):
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        print(username, password, code)
        # 1 先校验 验证码-忽略大小写
        if request.session.get('code').upper() == code.upper():
            # 2 校验用户、密码
            user_obj = auth.authenticate(request, username=username, password=password)
            if user_obj:
                # 保存用户状态
                auth.login(request, user_obj)
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名或密码错误'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


"""
图片相关模块 pillow
    1 图片普通操作
    2 对图片进行涂写
    
    Image：生成图片
    ImageDraw：在图片上涂画
    ImageFont：控制字体样式
"""
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO, StringIO

"""
内存管理器模块
    BytesIO：临时存储数据，返回数据为二进制
    StringIO：临时存储数据，返回数据为字符串
"""


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    # 推到步骤1：返回图片二进制数据
    # with open(r'static/img/111.png','rb') as f:
    #     data = f.read()
    #     print('data:', data)
    # return HttpResponse(data)

    # 推到步骤2：利用pillow动态产生图片
    # img_obj = Image.new('RGB', (260, 35), 'yellow')
    # img_obj = Image.new('RGB', (260, 35), (123,23,23))
    # img_obj = Image.new('RGB', (260, 35), get_random())  # 随机颜色
    # # 1 先将图片对象保存起来
    # with open('xxx.png', 'wb') as f:
    #     img_obj.save(f, 'png')
    # # 2 再将图片对象读取出来
    # with open('xxx.png', 'rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # 推到步骤3：步骤2文件存储繁琐，IO效率低 => 借助内存管理器模块
    # img_obj = Image.new('RGB', (260, 35), get_random())
    # io_obj = BytesIO() # 相当于一文件句柄
    # img_obj.save(io_obj, 'png')
    # return HttpResponse(io_obj.getvalue())  # 从内存管理器中读取二进制数据，返回给前端

    # 推到步骤4：写图片验证码
    img_obj = Image.new('RGB', (260, 40), get_random())  # 生成一张图片
    img_draw = ImageDraw.Draw(img_obj)  # 产生一个画笔对象
    img_font = ImageFont.truetype('static/font/aaa.ttf', 30)  # 字体样式

    # 随机验证码 5位数-数字、小写大写字母
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        # 上述3个中随机选一个
        tmp = random.choice([random_upper, random_lower, random_int])
        # 将产生的随机字符串写入图片
        """一个个写，可空间每一个的间距"""
        img_draw.text((i * 45 + 30, -2), tmp, get_random(), img_font)
        # 拼接字符串
        code += tmp
    print(code)
    # 随机验证码，在视图函数中用于比对 —— 存到视图函数可调用地方
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def home(request):
    # 查询本网站所有的文章展示到前端页面；使用分页器
    article_queryset = models.Article.objects.all()
    # -------------- 分页器 ------------------
    current_page = request.GET.get("page", 1)
    # 数据总条数
    all_count = article_queryset.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=10)
    # 2 直接对总数进行切片操作
    page_queryset = article_queryset[page_obj.start:page_obj.end]
    # ---------------------------------------
    return render(request, 'home.html', locals())


@login_required
def set_password(request):
    # 直接判断是否ajax请求
    if request.is_ajax():
        if request.method == 'POST':
            back_dic = {'code': 1000, 'msg': ''}
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # 校验密码
            is_right = request.user.check_password(old_password)
            if is_right:
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['msg'] = '修改成功'
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '两次密码不一致'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '原密码错误'
            return JsonResponse(back_dic)


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/home/')


def site(request, username, **kwargs):
    # 校验当前站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 用户不存在，返回404页面
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog  # jason对象

    # 查询个人站点所有文章返回
    article_list = models.Article.objects.filter(blog=blog)

    if kwargs:
        # print(kwargs)  # {'condition': 'tag', 'param': '1'}
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        # 判断用户想按照哪个条件筛选数据
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__id=param)
        elif condition == 'archive':
            year, month = param.split('-')  # 2020-11
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
        else:
            return render(request, 'error.html')

    # -------------- 分页器 ------------------
    current_page = request.GET.get("page", 1)
    # 数据总条数
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=10)
    # 2 直接对总数进行切片操作
    page_queryset = article_list[page_obj.start:page_obj.end]
    # ---------------------------------------

    """
    将下述代码制作成inclusion_tag 侧边栏目
    # 1 文章分类
        # 查询当前用户所有的分类 及 分类下的文章数目
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article')).values_list('name', 'count_num', 'pk')

    # 2 文章标签
        # 查询当前用户所有的标签 及 标签下的文章数目
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article')).values_list('name', 'count_num', 'pk')

    # 3 日期归档 - 按照年月统计所有的文章
    # date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month')  # 按month分组
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(count_num=Count('pk')).values_list('month', 'count_num')  # 按month分组
    """
    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    """
    先校验username和article_id是否存在，
    :param request:
    :param username:
    :param article_id:
    :return:
    """
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 获取文章对象
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()
    if not article_obj:
        return render(request, 'error.html')

    # 获取当前文章所有评论
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request, 'article_detail.html', locals())


import json
from django.db.models import F


def up_or_down(request):
    """
    处理点赞点踩
    1.校验用户是否登录
    2.判断当前文章是否是自己的写的（不能点自己的文章）
    3.当前用户是否已经点过赞（不能取消）
    4.操作数据库
    """
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}

        if request.method == 'POST':
            # 1.校验用户是否登录
            if request.user.is_authenticated:
                article_id = request.POST.get('article_id')
                is_up = request.POST.get('is_up')  # 字符串
                is_up = json.loads(is_up)  # 转换成boolean

                # 2.判断当前文章是否是自己的写的
                article_obj = models.Article.objects.filter(pk=article_id).first()
                if not article_obj.blog.userinfo == request.user:
                    print(request.user)

                    # 3.校验当前用户是否已经点过赞
                    is_click = models.UpAndDown.objects.filter(user=request.user, article=article_id)
                    if not is_click:
                        # 4.操纵数据库 同步操作article的普通字段
                        if is_up:
                            # 点赞+1
                            models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                            back_dic['msg'] = '点赞成功'
                        else:
                            # 点踩+1
                            models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                            back_dic['msg'] = '点踩成功'
                        # 操作点赞点踩表
                        models.UpAndDown.objects.create(user=request.user, article_id=article_id, is_up=is_up)
                    else:
                        back_dic['code'] = 1001
                        back_dic['msg'] = '你已点过，不能再点了'
                else:
                    back_dic['code'] = 1002
                    back_dic['msg'] = '臭不要脸的，不能给自己点'
            else:
                back_dic['code'] = 1003
                back_dic['msg'] = '请先<a href="/login/">登录</a/>'

            return JsonResponse(back_dic)


from django.db import transaction


def comment(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}

        if request.method == 'POST':
            # 后端再次判断用户是否登录
            if request.user.is_authenticated:
                article_id = request.POST.get('article_id')
                content = request.POST.get('content')
                parent_id = request.POST.get('parent_id')

                # 直接操作评论表 储存评论  两张表
                # 开启事务
                with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user, article_id=article_id, content=content,
                                                  parent_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '用户未登录'

            return JsonResponse(back_dic)


@login_required
def backend(request):
    """后台管理"""
    article_list = models.Article.objects.filter(blog=request.user.blog)
    # -------------- 分页器 ------------------
    current_page = request.GET.get("page", 1)
    # 数据总条数
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=10)
    # 2 直接对总数进行切片操作
    page_queryset = article_list[page_obj.start:page_obj.end]
    # ---------------------------------------
    return render(request, 'backend/backend.html', locals())


from bs4 import BeautifulSoup


@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')

        """处理xxs攻击：查找并删除script标签"""
        soup = BeautifulSoup(content, 'html.parser')

        tags = soup.find_all()  # 获取所有标签
        # 获取所有的标签
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()  # 删除标签

        # 文章简介 - 截取文本150字符
        # desc = content[:150]
        desc = soup.text[1:150]  # 简单处理-直接窃取content前150字符

        # 操作表，保存数据
        # 文章表
        article_obj = models.Article.objects.create(
            title=title,
            # content=content,
            content=str(soup),
            desc=desc,
            category_id=category_id,
            blog=request.user.blog
        )
        # 文章与标签的关系表 （半自动创建）不支持add set remove clear方法
        # 自己操作 - 多条数据 批量插入bulk_create
        article_obj_list = []
        for i in tag_id_list:
            tag_article_obj = models.Article2Tag(article=article_obj, tag_id=i)
            article_obj_list.append(tag_article_obj)
        # 批量插入数据
        models.Article2Tag.objects.bulk_create(article_obj_list)
        # 跳转后台管理 文章展示页
        return redirect('/backend/')

    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)
    return render(request, 'backend/add_article.html', locals())


import os
from django_bbs import settings

def upload_img(request):
    """
    需返回固定参数
    //成功时
        {
            "error" : 0,
            "url" : "http://www.example.com/path/to/file.ext"
        }
        //失败时
        {
            "error" : 1,
            "message" : "错误信息"
        }
    :param request:
    :return:
    """
    back_dic = {'error': 0}
    if request.method == 'POST':
        file_obj = request.FILES.get('imgFile')
        # 需手动储存图片
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        file_path = os.path.join(file_dir, file_obj.name)

        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)

        back_dic['url'] = '/media/article_img/%s' %file_obj.name

    return JsonResponse(back_dic)


def set_avatar(request):
    username = request.user.username
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar')
        # 手动加载前缀
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
        return redirect('/home/')
    return render(request, 'set_avatar.html', locals())