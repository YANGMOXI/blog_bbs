from django.db import models

# Create your models here.

"""
1 先写普通字段
2 再写外键字段
"""
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    phone = models.BigIntegerField(verbose_name='手机号', null=True, blank=True)
    """
    null=True   数据库该字段可以为空
    blank=True  admin后台管理该字段可以为空
    """
    avatar = models.FileField(upload_to='avatar', default='avatar/default.png', verbose_name='头像')
    """
    给avatar传文字对象，文件会自动存储到avatar文件夹下
        默认只保存avatar/default.png
    """
    create_time = models.DateField(auto_now_add=True)
    blog = models.OneToOneField(to='Blog', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '用户表'  # 修改admin后台管理默认的表名
        # verbose_name = '用户表'  # 末尾还是自动加s

    def __str__(self):
        return self.username


class Blog(models.Model):
    site_name = models.CharField(verbose_name='站点名称', max_length=32)
    site_title = models.CharField(verbose_name='站点标题', max_length=32)
    site_theme = models.CharField(verbose_name='站点样式', max_length=64)  # 存css/js文件路径

    def __str__(self):
        return self.site_name


class Category(models.Model):
    name = models.CharField(verbose_name='文章分类', max_length=32)
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name='文章标签', max_length=32)
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(verbose_name='文章标题', max_length=64)
    desc = models.CharField(verbose_name='文章简介', max_length=255)
    # 内容文字很多，一般用TextField
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateField(auto_now_add=True)

    # 字段设计优化
    up_num = models.BigIntegerField(verbose_name='点赞数', default=0)
    down_num = models.BigIntegerField(verbose_name='点踩数', default=0)
    comment_num = models.BigIntegerField(verbose_name='评论数', default=0)

    # 外键字段
    blog = models.ForeignKey(to='Blog', null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category', null=True, on_delete=models.DO_NOTHING)
    # 半自动创建第三章关系表，使用orm并方便拓展
    # tag = models.ManyToManyField(to='Tag', null=True)
    tags = models.ManyToManyField(to='Tag',
                                  through='Article2Tag',
                                  through_fields=('article', 'tag'),
                                  null=True)

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    """自建第三章关系表"""
    article = models.ForeignKey(to='Article',  on_delete=models.CASCADE)
    tag = models.ForeignKey(to='Tag',  on_delete=models.CASCADE)


class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo',  on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article',  on_delete=models.CASCADE)
    is_up = models.BooleanField()  # 传布尔值 0/1


class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo',  on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article',  on_delete=models.CASCADE)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    comment_time = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
    # 自关联
    # parent = models.ForeignKey(to="Comment", null=True)
    parent = models.ForeignKey(to="self", null=True,  on_delete=models.CASCADE)


