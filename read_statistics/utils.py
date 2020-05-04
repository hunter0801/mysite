from django.contrib.contenttypes.models import ContentType
from .models import ReadNum, ReadDetail
from django.utils import timezone
import datetime
from django.db.models import Sum

def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)
    if not request.COOKIES.get(key):
        # 总阅读数+1
        # if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
        #     # 存在记录
        #     readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk)
        # else:
        #     # 不存在
        #     readnum = ReadNum(content_type=ct, object_id=obj.pk)
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk) # 等价于上方的if else
        # 计数+1
        readnum.read_num += 1
        readnum.save()

        # 记录明细, 当天访问记录的统计，该表增加了一个日期信息
        date = timezone.now().date() # 获取当前时间
        readDetail,created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)# 记录存在则获取，记录不存在则创建实例
        readDetail.read_num += 1
        readDetail.save()
    return key

def get_seven_days_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = []
    for i in range(7,0,-1):
        date = today - datetime.timedelta(days=i) # 前 i 天的日期 timedelta可获得日期差
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type,date=date)
        result = read_details.aggregate(read_num_sum = Sum('read_num')) #实现聚合函数，对匹配的记录按照某一字段求和，返回字典类型
        read_nums.append(result['read_num_sum'] or 0)
    return dates,read_nums

def get_today_hot_data(content_type):
    """当天热门阅读博客的获取，filter过滤日期，按阅读量字段排序"""
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type,date=today).order_by('-read_num') # 降序排序
    return read_details[:7]

def get_yesterday_hot_data(content_type):
    """昨天热门阅读博客的获取，filter过滤日期，按阅读量字段排序"""
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type,date=yesterday).order_by('-read_num') # 降序排序
    return read_details[:7]

