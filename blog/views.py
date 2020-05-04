from django.shortcuts import render_to_response,get_object_or_404,render
from .models import Blog,BlogType
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from read_statistics.utils import read_statistics_once_read
from django.contrib.contenttypes.models import ContentType


# from datetime import datetime

def get_blog_list_common_data(request,blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)  # 通过分页器实现分页，每页10个
    page_num = request.GET.get('page', 1)  # 获取url页码参数GET请求，若无page属性，则默认1
    page_of_blogs = paginator.get_page(page_num)  # 根据前端用户的选择，展现第几页
    # 获取周围页码
    current_page_num = page_of_blogs.number
    page_range = list(range(max(1, current_page_num - 2), current_page_num)) + list(
        range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取博客分类的对应博客数量
    # BlogType.objects.annotate(blog_count=Count('blog')) #统计每个分类下blog的数量，记为blog_count

    # 获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time','month',order="DESC")
    blog_dates_dic = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_dates_dic[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs  # 将用户选择的页面对象放到模板中
    context['page_range'] = page_range
    # context['blogs_count'] = Blog.objects.all().count()
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['blog_dates'] = blog_dates_dic
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request,blogs_all_list)
    return render(request,'blog/blog_list.html', context)

def blogs_with_type(request,blog_type_pk):
    blog_type = get_object_or_404(BlogType,pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request,blogs_all_list)
    context['blog_type'] = blog_type
    return render(request,'blog/blogs_with_type.html', context)

def blogs_with_time(request,year,month):
    blogs_all_list = Blog.objects.filter(created_time__year=year,created_time__month=month)
    context = get_blog_list_common_data(request,blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year,month)
    return render(request,'blog/blogs_with_date.html', context)

def blog_detail(request,blog_pk):
    blog = get_object_or_404(Blog,pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request,blog)
    context = {}

    # 得到创建时间大于当前博客的查询集，找到其中最后一条，及为上一篇博客（所有博客按创建时间倒叙）
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    context['user'] = request.user
    # return render(request,'blog/blog_detail.html', context)
    response = render(request,'blog/blog_detail.html', context) # 响应
    response.set_cookie(read_cookie_key, 'true') #通知浏览器保存cookie为键值对 set_cookie(key,value,生存时长，到期时间)
    return response