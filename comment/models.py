from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import threading
from django.template.loader import render_to_string

class SendEmail(threading.Thread):
    """使用多线程，异步发送邮件"""
    def __init__(self,subject,text,email,fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            '',
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=self.fail_silently,
            html_message='self.text'
        )


class Comment(models.Model):
    """评论模型，包含评论用户，评论时间，评论内容，评论对象"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # 外键关联任何模型类（博客、动态等）
    object_id = models.PositiveIntegerField()  # 主键值
    content_object = GenericForeignKey('content_type', 'object_id')  #评论对象

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,related_name='comments',on_delete=models.CASCADE) # 外键关联用户模型，多对一，谁写的

    # 回复功能的新增字段
    ## 顶级评论
    root = models.ForeignKey('self',related_name='root_comment',null=True,on_delete=models.CASCADE)
    # parent_id = models.IntegerField(default=0) # 记录每一条评论的祖先id,没有祖先的默认为0
    ## 父级评论
    parent = models.ForeignKey('self',related_name='parent_comment',null=True,on_delete=models.CASCADE) # 设置外键指向自己，允许为空（顶级没有祖先）
    ## 二级及以上评论（回复）
    reply_to = models.ForeignKey(User,related_name='replies',null=True,on_delete=models.CASCADE) # 记录回复的谁，即祖先用户

    def send_email(self):
        # 发送邮件通知
        if not self.parent:
            ## 评论博客
            # 发送邮件
            subject = '有人评论你的博客'
            email = self.content_object.get_email()
        else:
            ## 回复评论
            subject = '有人回复你的评论'
            email = self.reply_to.email
        if email:
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = render_to_string('comment/send_email.html',context)
            send_mail = SendEmail(subject,text,email)
            send_mail.start()

    # 在后台管理页面，parent直接返回评论内容
    def __str__(self):
        return self.text

    class Meta:
        ordering = ['comment_time'] # 按照评论时间倒序


