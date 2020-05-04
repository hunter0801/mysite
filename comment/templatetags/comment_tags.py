# 写方法，该方法可以在html模板当标签来使用
from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Comment
from ..forms import CommentForm
register = template.Library()

@register.simple_tag()
def test(a):
    return 'this is test code:' + a

@register.simple_tag()
def get_comment_count(obj):
    """获取博客的评论数量"""
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()

@register.simple_tag()
def get_comment_form(obj):
    """获取评论表单"""
    content_type = ContentType.objects.get_for_model(obj)
    form =  CommentForm(initial={
        'content_type':content_type.model,
        'object_id':obj.pk,
        'reply_comment_id':0}) # 实例化并初始化
    return form

@register.simple_tag()
def get_comment_list(obj):
    """获取评论列表"""
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk,
                                      parent=None)  # 通过博客类型和主键值得到相应的评论记录,筛选一级评论
    return comments.order_by('-comment_time')