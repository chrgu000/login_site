# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from login import models,forms
from django.template.loader import get_template
import hashlib
from django.db.models import Q
# Create your views here.


def index(request):

    return render(request,'login/index.html')

def login(request):
    if request.session.get('is_login',None):
        return redirect('/index')

    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())

def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index/")

def addproduct(request):
    #如果没有登录,则无法通过输入地址方法登录.
    if not request.session.get('is_login',None):
        return redirect('/index')
    
    if request.method == 'POST':
        addproduct_form = forms.AddproductForm(request.POST,request.FILES)
        if addproduct_form.is_valid():
            addproduct_form.save()
            message = "您提交的信息已存储"

        else:
            message = '请完善产品信息'
            return render(request, 'addproduct.html', locals())
    else:
        addproduct_form = forms.AddproductForm()
        message = '请填写产品信息'
    return render(request, 'addproduct.html', locals())

def inventory(request):
    #如果没有登录,则无法通过输入地址方法登录.
    if not request.session.get('is_login',None):
        return redirect('/index')
    products = models.Product.objects.all()
    return render(request, 'inventory.html', locals())

def detail(request,id):
    #如果没有登录,则无法通过输入地址方法登录.
    if not request.session.get('is_login',None):
        return redirect('/index')

    try:
        product = models.Product.objects.get(id=id)
    except:
        pass
    return render(request, 'detail.html', locals())

def search(request):
    q = request.GET.get('q')
    error_msg = ''
    if not q:
        return redirect('/inventory')
        
    post_list = models.Product.objects.filter(Q(nickname__icontains=q)|
                Q(feature__icontains=q)|Q(description__icontains=q))
    return render(request, 'result.html', {'post_list':post_list})

# def result(request):
    















def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode()) # update方法只接收bytes类型
    return h.hexdigest()