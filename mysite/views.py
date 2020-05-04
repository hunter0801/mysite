import datetime
from django.shortcuts import render_to_response,render,redirect
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from read_statistics.utils import get_seven_days_data,get_today_hot_data,get_yesterday_hot_data
from blog.models import Blog
from django.urls import reverse  # 反向




def get_7_days_hot_blog():
    """前7天热门阅读博客的获取，通过关联模型，可以由blog模型获得readdetail中的信息，对日期段内的数据分组并统计阅读量，按阅读量字段排序"""
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects \
        .filter(read_details__date__lt=today,read_details__date__gte=date) \
        .values('id','title') \
        .annotate(read_num_sum=Sum('read_details__read_num')) \
        .order_by('-read_num_sum')
    return blogs[:7]

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_data(blog_content_type)

    # 获取七天热门缓存数据
    hot_blogs_for_7_days = cache.get('hot_blogs_for_7_days')
    if not hot_blogs_for_7_days:
        hot_blogs_for_7_days = get_7_days_hot_blog()
        cache.set('hot_blogs_for_7_days',hot_blogs_for_7_days, 3600)

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['hot_blogs_for_7_days'] = hot_blogs_for_7_days
    return render(request,'home.html',context) # 模板文件在templates下

