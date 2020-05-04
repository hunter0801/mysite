from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation # 关联模型，不需要重新迁移表
from ckeditor_uploader.fields import RichTextUploadingField # 可插入图片
from read_statistics.models import ReadNumExpendMethod, ReadDetail
from django.urls import reverse

class BlogType(models.Model):
    """分类模型"""
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name  # 后台管理界面时，显示分类名称

class Blog(models.Model, ReadNumExpendMethod): # 继承获取阅读量的父类
    """博文模型"""
    title = models.CharField(max_length=50)
    blog_type = models.ForeignKey(BlogType,on_delete=models.CASCADE) # 博文与分类模型多对一，外键相连，删除分类时连带博文删除
    # content = models.TextField()
    content = RichTextUploadingField() # 内容更改为富文本编辑器类型
    author = models.ForeignKey(User,on_delete=models.CASCADE) #博文与作者模型多对一，外键相连，删除博文不影响作者
    # readed_num = models.IntegerField(default=0)
    read_details = GenericRelation(ReadDetail) # 通过Blog模型可以访问到其关联模型ReadDetail的数据
    created_time= models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now_add=True)

    '''def get_read_num(self): #定义返回阅读数量的方法，readnum是关联模型类的小写
        try:
            return self.readnum.read_num
        except exceptions.ObjectDoesNotExist: # 如果错误类型为不存在该对象则返回0
            return 0
    '''
    def get_url(self):
        """根据具体类型给出链接"""
        return reverse('blog_detail',kwargs={'blog_pk':self.pk})

    def get_email(self):
        """根据类型给出email"""
        return self.author.email

    def __str__(self): #后台管理页面，博文显示博文的标题
        return "<Blog: %s>" % self.title

    class Meta: # 排序规则
        ordering = ['-created_time']

'''class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)
    blog = models.OneToOneField(Blog,on_delete=models.CASCADE) #一对一，删除阅读记录不会对原博客有影响
'''


