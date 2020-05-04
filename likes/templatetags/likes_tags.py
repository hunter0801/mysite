# 写方法，该方法可以在html模板当标签来使用
from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import LikeCount,LikeRecord
register = template.Library()

@register.simple_tag()
def get_like_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    like_count, created = LikeCount.objects.get_or_create(content_type=content_type,object_id=obj.pk )
    return like_count.liked_num

@register.simple_tag(takes_context=True) # 可以使用所在模板页的一些变量
def get_like_status(context,obj):
    """根据是否存在点赞记录，显示红色"""
    content_type = ContentType.objects.get_for_model(obj)
    user = context['user']
    if not user.is_authenticated:
        return ''
    if LikeRecord.objects.filter(content_type=content_type,object_id=obj.pk,user=user).exists():
        return 'active'
    else:
        return ''


@register.simple_tag
def get_content_type(obj):
    """获得当前的模型类名字"""
    content_type = ContentType.objects.get_for_model(obj)
    return content_type.model