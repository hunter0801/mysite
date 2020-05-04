from django.shortcuts import render,redirect
from django.contrib.contenttypes.models import ContentType
from .models import Comment
from django.urls import reverse
from .forms import CommentForm
from django.http import JsonResponse

def update_comment(request):
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    comment_form = CommentForm(request.POST,user=request.user) # 传参，进行用户验证
    data = {}
    if comment_form.is_valid():
        # 检查通过，保存数据
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']
        comment.save()

        ## 对回复内容进行处理,并将回复保存进数据库
        parent = comment_form.cleaned_data['parent']
        if parent: # 说明为回复操作
            comment.root = parent.root if parent.root else parent # 如果该回复的祖先根为0，说明祖先没有祖先了，直接把祖先设为根
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()

        # 发送邮件通知
        comment.send_email()


        # 返回数据
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.get_nickname_or_username()
        # data['comment_time'] = comment.comment_time.strftime("%Y-%m-%d %H:%M:%S") # 需要将日期类型转为字符串
        data['comment_time'] = comment.comment_time.timestamp() # 传入时间戳
        data['text'] = comment.text
        data['content_type'] = ContentType.objects.get_for_model(comment).model
        if parent:# 有祖先时，显示祖先
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ' '
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if comment.root else ''
        # return redirect(referer)
    else:
        # return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.value())[0][0] # 选择第一个错误信息抛出
    return JsonResponse(data)