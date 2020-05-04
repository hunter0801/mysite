from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget
from .models import Comment

class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)# 这两个字段隐藏，只留下text
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'),error_messages={'required':'评论内容不能为空'}) # 可换行

    # 增加回复id，若为顶级评论则初始化为0
    reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id':'reply_comment_id'}))

    def __init__(self,*args,**kwargs):
        if 'user' in kwargs: # 获取user关键字参数
            self.user = kwargs.pop('user')
        super(CommentForm,self).__init__(*args,**kwargs)

    def clean(self):
        """验证"""

        # 判断用户是否登录
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 评论对象验证
        content_type = self.cleaned_data['content_type']
        object_id = self.cleaned_data['object_id']
        model_class = ContentType.objects.get(model=content_type).model_class()  # 得到博客的contenttype类型，然后由类型得到blog模型类
        model_obj = model_class.objects.get(pk=object_id)  # 由blog模型类得到匹配的博客记录

        try:
            model_class = ContentType.objects.get(model=content_type).model_class()
            object_obj = model_class.objects.get(pk=object_id)
            self.cleaned_data['content_object'] = model_obj # 返回相应模型类对象
        except ObjectDoesNotExist as e:
            raise forms.ValidationError('评论对象不存在')
        return self.cleaned_data

    def clean_reply_comment_id(self):
        reply_comment_id = self.cleaned_data['reply_comment_id']
        if reply_comment_id < 0 :                #
            raise forms.ValidationError('回复出错')
        elif reply_comment_id ==  0:    # 说明此条评论为一级评论
            self.cleaned_data['parent'] = None
        elif Comment.objects.filter(pk=reply_comment_id).exists():    # 非一级评论查看，要回复的评论是否存在
            self.cleaned_data['parent'] = Comment.objects.get(pk=reply_comment_id)
        else:
            raise forms.ValidationError('回复出错')      # 要回复的对象不存在
        return reply_comment_id
