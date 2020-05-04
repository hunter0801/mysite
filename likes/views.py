from django.shortcuts import render
from .models import LikeCount,LikeRecord
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist



def ErrorResponse(code,message):
    """点赞的错误信息返回"""
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)

def SuccessResponse(liked_num):
    """点赞成功返回成功状态和点赞数量"""
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)

def like_change(requset):
    """点赞请求的处理流程"""
    ## 获取数据
    user = requset.user
    ### 验证点赞用户是否存在
    if not user.is_authenticated:
        return ErrorResponse(400,'you were not login')

    content_type = requset.GET.get('content_type')
    object_id = int(requset.GET.get('object_id'))
    is_like = requset.GET.get('is_like')

    ### 验证被点赞对象、id是否存在
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401,'object not exist')

    ## 处理数据
    if is_like == 'true':
        # 要点赞
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type,object_id=object_id,user=user)
        if created:
            # 未点赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return SuccessResponse(like_count.liked_num)
        else:
            # 已点赞过，不能重复点赞
            return ErrorResponse(402,'you were liked')
    else:
        # 取消点赞
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id,user=user).exists():
            # 有点赞过，取消点赞
            like_record = LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            # 点赞总数-1
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()
                return SuccessResponse(like_count.liked_num)
            else:
                return ErrorResponse(404, 'data error')
        else:
            # 没有点赞过，不能取消
            return ErrorResponse(403,'you were not liked')

