from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model): # 简介
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20,verbose_name='昵称')

    def __str__(self):
        return '<Profile: %s for %s>' % (self.nickname,self.user.username)

def get_nickname(self):
    """动态绑定"""
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return ''

def get_nickname_or_username(self):
    """动态绑定"""
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return self.username

def has_nickname(self):
    return Profile.objects.filter(user=self).exists()

User.get_nickname = get_nickname
User.has_nickname = has_nickname
User.get_nickname_or_username = get_nickname_or_username
