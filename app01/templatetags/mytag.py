# -*- coding: utf-8 -*-
# date: 2020/10/7 15:54

from django import template
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth


register = template.Library()


# 自定义inclusion_tag
@register.inclusion_tag('left_menu.html')
def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 1 文章分类
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article')).values_list('name', 'count_num', 'pk')
    # 2 文章标签
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article')).values_list('name', 'count_num', 'pk')
    # 3 日期归档
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(count_num=Count('pk')).values_list('month', 'count_num')  # 按month分组

    return locals()
