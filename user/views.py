import string
import random
import time
from django.shortcuts import render,redirect
from django.contrib import auth
from django.urls import reverse  # 反向
from django.core.mail import send_mail
from .forms import LoginForm, RegForm,ChangeNicknameForm,BindEmailForm,ChangePasswordForm,ForgotPasswordForm# 表单类
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Profile

def login_for_modal(request):
    """ajax登录的处理方法"""
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():  # 验证操作在forms.py里，验证通过在视图函数中进行登录
        user = login_form.cleaned_data['user']  # 获取验证之后的用户字段数据
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'SUCCESS'
        return JsonResponse(data)

def login(request):
    # username = request.POST.get('username','') # post方法返回字典,获取不到设为空
    # password = request.POST.get('password','')
    # # 验证
    # user = auth.authenticate(request,username=username,password=password) # 认证成功则返回真
    # referer = request.META.get('HTTP_REFERER',reverse('home')) # HTTP请求头中记录了登录之前的页面信息，获取不到则跳转到首页(通过别名解析得到链接)
    # if user:
    #     auth.login(request, user)
    #     return redirect(referer) # 重定向
    # else:
    #     return render(request,'error.html',{'message':'用户名或密码不正确'})
    if request.method == 'POST':
        login_form = LoginForm(request.POST)      # 实例化表单数据
        if login_form.is_valid():                 # 验证操作在forms.py里，验证通过在视图函数中进行登录
            user = login_form.cleaned_data['user']  # 获取验证之后的用户字段数据
            auth.login(request, user)
            return redirect(request.GET.get('form',reverse('home'))) # 重定向到由get方法传入的原路径，没有则跳转到首页
    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'user/login.html', context)

def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST,request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            # 创建用户
            user = User.objects.create_user(username,email,password)
            user.save()
            # 清除session，避免反复使用同一验证码进行验证
            del request.session['register_code']

            # 登录用户
            user = auth.authenticate(username=username,password=password)
            auth.login(request,user)

    else:
        reg_form = RegForm()

    context = {}
    context['reg_form'] = reg_form
    return render(request, 'user/register.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('form', reverse('home')))  # 重定向到由get方法传入的原路径，没有则跳转到首页

def user_info(request):
    context = {}
    return render(request, 'user/user_info.html', context)

def change_nickname(request):
    redirect_to = request.GET.get('from',reverse('home'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST,user=request.user)
        if form.is_valid(): # 判断提交新昵称是否为空，是否已登录
            nickname_new = form.cleaned_data['nickname_new']
            profile,created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    context = {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request,'form.html',context)

def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))

    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():  # 判断提交新昵称是否为空，是否已登录
            # 绑定
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            # 清除session，避免反复使用同一验证码进行验证
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/bind_email.html', context)

def send_verification_code(request):
    email = request.GET.get('email','')
    send_for = request.GET.get('send_for','')
    data = {}

    if email:
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits,4))
        # 记录发邮件的时间
        now = int(time.time())
        send_code_time = request.session.get('send_code_time',0)
        if now - send_code_time < 60:
            data['status'] = 'ERROR'
        else:
            request.session[send_for] = code  # 验证码存储为session列表
            request.session['send_code_time'] = now

            # 发送邮件
            send_mail(
                '绑定邮箱',
                '验证码：%s' % code,
                '1130266522@qq.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():  # 判断提交新昵称是否为空，是否已登录
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)

def forgot_password(request):
    redirect_to = reverse('login')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():  # 判断提交新昵称是否为空，是否已登录
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除session，避免反复使用同一验证码进行验证
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = {}
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '重置'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/forgot_password.html', context)

