from django.contrib import admin
from .models import BlogType, Blog

@admin.register(BlogType) #将类别进行注册
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name') #定义数据列表中显示哪些字段

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    '''list_display = ('title','blog_type','author','get_read_num','created_time','last_updated_time')'''
    list_display = ('id','title', 'blog_type', 'author','get_read_num', 'created_time', 'last_updated_time')
'''@admin.register(ReadNum)
class ReadNumAdmin(admin.ModelAdmin):
    list_display = ('read_num','blog')
'''