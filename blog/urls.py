from django.urls import path
from . import views

urlpatterns = [
    path('',views.blog_list,name='blog_list'),
    # localhost:8000/blog/1,整型的编号
    path('<int:blog_pk>',views.blog_detail,name="blog_detail"),
    path('type/<int:blog_type_pk>',views.blogs_with_type,name="blogs_with_type"),
    path('date/<int:year>/<int:month>',views.blogs_with_time,name="blogs_with_time"),
]