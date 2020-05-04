from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import exceptions # 引入错误集合
from django.utils import timezone

class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) # 外键对应模型类
    object_id = models.PositiveIntegerField() # 主键值
    content_object = GenericForeignKey('content_type','object_id')

class ReadNumExpendMethod():
    '''获取对应阅读量的方法，总的阅读量'''
    def get_read_num(self):
        try:
            ct = ContentType.objects.get_for_model(self)
            readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)
            return readnum.read_num
        except exceptions.ObjectDoesNotExist:
            return 0

class ReadDetail(models.Model):
    """访问记录明细，每天的阅读信息"""
    date = models.DateField(default=timezone.now) # 记录每天的日期信息
    read_num = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # 外键对应模型类
    object_id = models.PositiveIntegerField()  # 主键值
    content_object = GenericForeignKey('content_type', 'object_id')