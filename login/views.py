# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.db import transaction
from login import models,forms
from django.template.loader import get_template
import hashlib
from django.db.models import Q,Sum
from django.views.generic import View
# from pure_pagination import Paginator,EmptyPage,PageNotAnInteger
from django.core.paginator import Paginator,EmptyPage
import time,os,json
import xlrd,xlwt
from random import randint
import collections

def getTime():
    timeNow = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return timeNow


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
            code = register_form.cleaned_data['secret_code']
            print code
            if code != 'sportslinque':
                error_msg ="请输入正确口令"
                return render(request,'error.html',locals())
            else:
                pass
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

    return redirect("/index/")
    # return HttpResponse("<a href="/index/">index</a>")

def addproduct(request):
    #如果没有登录,则无法通过输入地址方法登录.
    if not request.session.get('is_login',None):
        return redirect('/index')
    
    if request.method == 'POST':
        addproduct_form = forms.AddproductForm(request.POST,request.FILES)
        if addproduct_form.is_valid():
            # print addproduct_form
            # for index in addproduct_form:
                # print index
            addproduct_form.save()
            message = "您提交的信息已存储"

        else:
            message = '请完善产品信息'
            return render(request, 'addproduct.html', locals())
        product_obj = models.Product.objects.latest('id')
        print product_obj
    else:
        addproduct_form = forms.AddproductForm()
        message = '请填写产品信息'
    return render(request, 'addproduct.html', locals())

class UploadproductView(View):
    def get(self,request):
        message = "请填写表单并选择上传文件" 
        return render(request,'uploadproduct.html',locals())
    
    def post(self,request):
        uploaduser = request.POST.get('uploaduser')
        date = request.POST.get('date')
        File = request.FILES.get('files',None)
        
        if File is None or uploaduser is None or date is None:
            return HttpResponse("请填写表单")
            
        else:
            type_excel = File.name.split('.')[-1]
            if 'xlsx' == type_excel:
                upload_obj = models.Uploadfiles.objects.create(uploaduser=uploaduser,date=date,file_name=File.name)
                wb = xlrd.open_workbook(filename=None,file_contents=File.read())
                table = wb.sheets()[0]
                nrows = table.nrows
                try:
                    with transaction.atomic():
                        for i in range(1,nrows):
                            rowValues = table.row_values(i)
                            models.Product.objects.create(nickname=rowValues[0],feature=rowValues[1],uniqueid=rowValues[2])
                    num = nrows-1
                    uploadproducts = models.Product.objects.order_by('-id')[:num]
                    return render(request,'uploadproduct.html',locals())
                except Exception as e:
                    return HttpResponse("出现错误")
            else:
                return HttpResponse("上传文件格式不是xlsx")

def orderspecify(order,specify):
    if order == "Positive":
        specify = specify
    else:
        specify = "-"+specify
    return specify

class InventoryView(View):
    #包含了排序,檢索功能的庫存顯示頁.

    def get(self,request):
        #解决了通过登录信息session获取用户的操作.
        try:
            user = request.session.get('user_name','None')
            user_obj = models.User.objects.get(name=user)
            # print user_obj.name
        except:
            pass
            # print "no user"
        
        products = models.Product.objects.all()
        # sort = request.GET.get('sort','')
        q = request.GET.get('q','')
        order = request.GET.get('order','')
        specify = request.GET.get('specify','')

        if q:
            products = products.filter(Q(nickname__icontains=q)| Q(feature__icontains=q)|Q(description__icontains=q))
        else:
            pass
        
        # mm = orderspecify(order,specify)
        # print mm
        if specify == "id":
            products = products.order_by(orderspecify(order,specify))
        elif specify == 'count':
            products = products.order_by(orderspecify(order,specify))
        else:
            pass
        
        paginator = Paginator(products,10)
        try:
            current_num = int(request.GET.get('page',1))
            products = paginator.page(current_num)
        except EmptyPage:
            products = paginator.page(1)
        
        if paginator.num_pages > 11:
            if current_num -5 <1:
                pageRange =range(1,11)
            elif current_num + 5>paginator.num_pages:
                pageRange = range(current_num-5,current_num+1)
            else:
                pageRange = range(current_num-5,current_num+6)
        else:
            pageRange = range(1,paginator.num_pages+1)

        return render(request,'inventory.html',locals())


def search(request):
    q = request.GET.get('q')
    error_msg = ''
    if not q:
        return redirect('/inventory')
        
    post_list = models.Product.objects.filter(Q(nickname__icontains=q)|
                Q(feature__icontains=q)|Q(description__icontains=q))
    return render(request, 'result.html', {'post_list':post_list})

def detail(request,id):
    #如果没有登录,则无法通过输入地址方法登录.
    if not request.session.get('is_login',None):
        return redirect('/index')

    try:
        product = models.Product.objects.get(id=id)
    except:
        pass
    return render(request, 'detail.html', locals())



class InventoryMaterial(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
            
        inventorymaterials = models.InventoryMaterial.objects.all().order_by('id')
        sort = request.GET.get('sort','') #排序方式
        print sort
        q = request.GET.get('q','') #检索内容
        total_amount_obj = models.InventoryMaterial.objects.values('amount').aggregate(num=Sum('amount'))#总库存
        total_amount = total_amount_obj['num']
        #检索部分的选择
        if q:
            inventorymaterials = inventorymaterials.filter(Q(uniqueId__icontains=q) | 
                Q(description__icontains=q) | Q(amount__icontains=q))
        else:
            pass
        #排序部分
        if sort:
            if sort == 'amountincrease':
                inventorymaterials = inventorymaterials.order_by('amount')
            elif sort == 'amountdecrease':
                inventorymaterials = inventorymaterials.order_by('-amount')
            elif sort == 'uid':
                inventorymaterials = inventorymaterials.order_by('uniqueId')
            else:
                pass
        else:
            pass
            
        #分页部分
        paginator = Paginator(inventorymaterials,20)
        try:
            current_num = int(request.GET.get('page',1))
            inventorymaterials = paginator.page(current_num)
        except EmptyPage:
            inventorymaterials = paginator.page(1)
        if paginator.num_pages > 11:
            if current_num -5 <1:
                pageRange =range(1,11)
            elif current_num + 5>paginator.num_pages:
                pageRange = range(current_num-5,current_num+1)
            else:
                pageRange = range(current_num-5,current_num+6)
        else:
            pageRange = range(1,paginator.num_pages+1)
            
        return render(request,"inventorymaterial.html",locals())




    
def inventoryDetail(request,id):
    if not request.session.get('is_login',None):
        return redirect('/index')
    try:
        inventorymaterial = models.InventoryMaterial.objects.get(id=id)
    except:
        pass
    return render(request, 'inventorydetail.html', locals())

class Inventoryinit(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写物料库存信息"
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        return render(request,'inventoryinit.html',locals())
        
    def post(self,request):
        new_amount = request.POST.get('amount')
        new_description = request.POST.get('description')
        new_uid = request.POST.get('uniqueid')
        new_user = request.session.get('user_name','None')
        new_image = request.FILES.get('image',None)
        new_price = request.POST.get('price')
        pageNow = "新增物料页"
        
        if new_amount=="" or new_description=="" or new_uid=="" :
            error_msg ="未完整填写表单"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        elif not new_image:
            error_msg ="未上传物料图片"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        else:
            uid_exist = models.InventoryMaterial.objects.filter(uniqueId = str(new_uid))
            if uid_exist :
                error_msg = new_uid+":唯一识别码重复"
                addErrorlog(request,error_msg,pageNow)
                return render(request,'error.html',locals())
            
            else:
                user_obj = models.User.objects.get(name=new_user)
                material_obj = models.InventoryMaterial.objects.create(amount=new_amount,description=new_description,\
                            uniqueId=new_uid,userPurchase=user_obj,image=new_image,price=new_price)
                
                message = "录入成功"

                _act = "新增物料:"+new_uid
                models.AutoLog.objects.create(date=getTime(),user=user_obj,act=_act)
                return render(request,'inventoryinit.html',locals())





def inStock(request):
    if not request.session.get('is_login',None):
        return redirect('/index')
    instocks = models.InStock.objects.all().order_by('-id')
    return render(request,"instock.html",locals())

def inStockDetail(request,id):
    if not request.session.get('is_login',None):
        return redirect('/index')
    try:
        #通过instock的id找出对象
        instock = models.InStock.objects.get(id=id)
        #1对多的对象
        initems = models.InItem.objects.filter(master=id)

    except:
        pass
    return render(request, 'instockdetail.html', locals())

        
class Instockadd(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写表单并选择物料"
        #user直接从登陆人获取
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        lastcode = models.InStock.objects.all().order_by('-id')[0].code   
        return render(request,'instockadd.html',locals())
    
    def post(self,request):
        new_code = request.POST.get('code')
        new_c_time = request.POST.get('c_time')
        new_description = request.POST.get('description')
        
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        
        pageNow = "新增入库页"
        # if new_code is None or new_c_time is None or new_description is None:
        if new_code == "" or new_c_time == "" or new_description == "":
            error_msg ="未完整填写表单"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        
        else:
            # 对code查重
            code_exist = models.InStock.objects.filter(code__contains = str(new_code))
            if code_exist:
                error_msg = new_code+":入库编号重复"
                addErrorlog(request,error_msg,pageNow)
                return render(request,'error.html',locals())
            else:
                instock_obj = models.InStock.objects.create(code=new_code,c_time=new_c_time,description=new_description,userInstock=user_obj)
                print "Instock create"
                
                # InItem是1对多模型,取出每一组值,找出InStock和material_obj的对象,创建InItem对象并插入数据
                items = request.POST.getlist('item')
                itemamounts = request.POST.getlist("itemamount")
                
                for item,itemamount in zip(items,itemamounts):
                    # 避免存在空值
                    if item == u'' or itemamount == u'':
                        pass
                    else:
                        item_id = int(item)
                        item_amount = abs(int(itemamount))
                        material_obj = models.InventoryMaterial.objects.get(id=item_id)
                        # 根据入库的数量修改库存数量
                        material_obj.amount += item_amount
                        material_obj.save()
                        item_object = models.InItem.objects.create(master=instock_obj,materialName=material_obj,amountIn=item_amount)

        _act = "新增入库:"+new_code
        models.AutoLog.objects.create(date=getTime(),user=user_obj,act=_act)
        return render(request, 'instockadd.html', locals()) 
        
    

def inItem(request):
    inventorymaterials = models.InventoryMaterial.objects.all().order_by("uniqueId")
    return render(request,"initem.html",locals())

def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode()) # update方法只接收bytes类型
    return h.hexdigest()

class Uploadmaterial(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写表单并选择上传文件"
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        date = getTime()
        lastcode = models.InStock.objects.all().order_by('-id')[0].code   
        return render(request,'uploadmaterial.html',locals())
    
    def post(self,request):
        
        new_c_time = request.POST.get('c_time')#对应date
        new_code = request.POST.get('code')#对应modifyindex
        new_description = request.POST.get('description')
        File = request.FILES.get('files',None)
        pageNow = "批量新增/入库页"

        if File is None or new_c_time == "" or new_code == "":
            
            error_msg ="未完整填写表单"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        else:
            # 对code查重
            code_exist = models.InStock.objects.filter(code__contains = str(new_code))
            if code_exist:
                error_msg =new_code+":入库编号重复"
                addErrorlog(request,error_msg,pageNow)
                return render(request,'error.html',locals())
            
            else:
                #创建instock对象
                user = request.session.get('user_name','None')
                user_obj = models.User.objects.get(name=user)
                instock_obj = models.InStock.objects.create(code=new_code,c_time=new_c_time,description=new_description,userInstock=user_obj)
                _act = "批量新增/入库物料,入库编号:"+new_code
                models.AutoLog.objects.create(date=getTime(),user=user_obj,act=_act)
                
                type_excel = File.name.split('.')[-1] 
                if 'xlsx'== type_excel:
                    upload_obj = models.Uploadfiles.objects.create(uploaduser=user_obj.name,date=new_c_time,file_name=File.name)
                    wb = xlrd.open_workbook(filename=None,file_contents=File.read())
                    table = wb.sheets()[0]
                    nrows = table.nrows
                    # print upload_obj
                    rowValues = table.row_values(0)
                    tag = rowValues[0]
                    if tag != "instocktable":
                        instock_obj.delete()
                        error_msg =str(File.name)+":未识别到入库/新建物料excel标准模板,入库编号"+str(new_code)+"可继续使用"
                        addErrorlog(request,error_msg,pageNow)
                        return render(request,'error.html',locals())
                         #既然失败,就把对象删了.
                        
                    else:
                        pass
                    try:
                        with transaction.atomic():
                            for i in range(2,nrows):
                                rowValues = table.row_values(i)
                                uniq = rowValues[0]
                                purchaseuser = rowValues[3]
                                _price = rowValues[4]
                                _amount = rowValues[2]
                                get_price,tag_p = judgeinput(_price)
                                get_amount,tag_a = judgeint(_amount)
                                #user是外键,找出对应的对象
                                uniq_obj = models.InventoryMaterial.objects.filter(uniqueId=uniq)
                                # print uniq_obj

                                #如果uniqID重复了,说明是追加入库,只修改数量
                                if uniq_obj:
                                    #用filter找出的对象无法存储,只好用get再取一次
                                    #uniq_get是物料对象
                                    uniq_get = models.InventoryMaterial.objects.get(uniqueId=uniq)
                                    uniq_get.amount += get_amount
                                    uniq_get.save()
                                #如果不重复,说明是首次,创建新的物料对象
                                else:
                                    userPur = models.User.objects.filter(name = purchaseuser)
                                    if rowValues[0] and rowValues[1] and userPur:
                                        models.InventoryMaterial.objects.create(uniqueId=rowValues[0],description=rowValues[1],
                                            amount=get_amount,userPurchase=userPur[0],price=get_price)
                                    else:
                                        j=i+1
                                        error_msg ="第"+str(j)+"行存在缺项,入库编号"+str(new_code)+"已占用,请新建"
                                        addErrorlog(request,error_msg,pageNow)
                                        return render(request,'error.html',locals())
                                material_obj = models.InventoryMaterial.objects.get(uniqueId=uniq)
                                item_object = models.InItem.objects.create(master=instock_obj,materialName=material_obj,amountIn=get_amount)
                                print "create initem object"
                            
                            message = "已完成上传,请在入库详情中查看."
                            
                            return render(request,'uploadmaterial.html',locals())

                    except Exception as e:
                        error_msg ="上传文件出现未定义错误"
                        addErrorlog(request,error_msg,pageNow)
                        return render(request,'error.html',locals())
                else:
                    error_msg =str(File.name)+":上传文件格式不是xlsx"
                    addErrorlog(request,error_msg,pageNow)
                    return render(request,'error.html',locals())


class Productlist(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        producttemps = models.ProductTemp.objects.all().order_by('id')

        q = request.GET.get('q','') #检索内容
        order = request.GET.get('order','')
        specify = request.GET.get('specify','')
        print specify
        
        #检索部分的选择
        if q:
            producttemps = producttemps.filter(Q(title__icontains=q) | Q(sku__icontains=q) | Q(childAsin__icontains=q) \
               | Q(description__icontains=q))
        else:
            pass
            
        #排序部分
        if specify == "id":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "purchasePrice":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "dhlShippingFee":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "shrinkage":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "amazonSalePrice":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "margin":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "marginRate":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "productCostPercentage":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "description":
            producttemps = producttemps.order_by(orderspecify(order,specify))


        #分页部分
        paginator = Paginator(producttemps,10)
        try:
            current_num = int(request.GET.get('page',1))
            producttemps = paginator.page(current_num)
        except EmptyPage:
            producttemps = paginator.page(1)
        if paginator.num_pages > 11:
            if current_num -5 <1:
                pageRange =range(1,11)
            elif current_num + 5>paginator.num_pages:
                pageRange = range(current_num-5,current_num+1)
            else:
                pageRange = range(current_num-5,current_num+6)
        else:
            pageRange = range(1,paginator.num_pages+1)
        _act = "浏览产品页"+" 搜索: "+q
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        models.AutoLog.objects.create(date=getTime(),user=user_obj,act=_act)
        return render(request,"productlist.html",locals())

def calDHLShippingFee(weight,length,width,height):
    weight = float(weight)
    length = float(length)
    width = float(width)
    height = float(height)
    fee1 = weight*35
    fee2 = length*width*height*0.007
    if fee1 >= fee2 :
        return fee1
    else:
        return fee2
    
def calShrinkage(purprice,dhlfee,packfee,opfee,currency,fbafee,adcost):
    purprice = float(purprice)
    dhlfee = float(dhlfee)
    packfee = float(packfee)
    opfee = float(opfee)
    currency = float(currency)
    fbafee = float(fbafee)
    adcost= float(adcost)
    fee1 = (purprice +dhlfee+packfee+opfee)/currency
    fee2 = (fee1+fbafee+adcost)*0.117
    return fee2

def calMargin(purprice,dhlfee,packfee,opfee,currency,fbafee,shrinkage,adcost,amazonfee,payonfee,amazonprice):
    purprice = float(purprice)
    dhlfee = float(dhlfee)
    packfee = float(packfee)
    opfee = float(opfee)
    currency = float(currency)
    fbafee = float(fbafee)
    adcost= float(adcost)
    amazonfee =float(amazonfee)
    payonfee = float(payonfee)
    amazonprice=float(amazonprice)
    shrinkage = float(shrinkage)
    fee1 = amazonprice*(1-amazonfee/100)
    fee2 = fbafee+shrinkage+adcost
    fee3 = (fee1-fee2)*(1-payonfee/100)*currency
    fee4 = fee3-purprice-dhlfee-packfee-opfee #margin
    if amazonprice*currency==0:
        fee5 = 0
    else:
        fee5 = 100*fee4/(amazonprice*currency)#marginrate
    return fee4,fee5

def calProductCostPercentage(purprice,amazonprice,currency):
    purprice = float(purprice)
    amazonprice=float(amazonprice)
    currency = float(currency)
    if amazonprice*currency==0:
        fee=0
    else:
        fee = 100*purprice/(amazonprice*currency)
    return fee


class Addproducttemp(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写表单"
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        sites = models.Site.objects.all()
        return render(request,'addproducttemp.html',locals())
        
    def post(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
            
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        
        new_sku = request.POST.get("sku")
        new_childasin = request.POST.get("childasin")
        new_title = request.POST.get("title")
        new_description = request.POST.get("description")
        new_site = request.POST.get("site")
        new_date = request.POST.get("c_time")
        
        purchaseprice = request.POST.get("purchaseprice")
        weight = request.POST.get("weight")
        length = request.POST.get("length")
        width = request.POST.get("width")
        height = request.POST.get("height")
        volumeweight = request.POST.get("volumeweight")
        
        packagefee = request.POST.get("packagefee")
        opfee = request.POST.get("opfee")
        currency = request.POST.get("currency")
        fbafee = request.POST.get("fbafee")
        amazonfee = request.POST.get("amazonfee")
        payserfee = request.POST.get("payserfee")
        adcost = request.POST.get("adcost")
        amazonprice = request.POST.get("amazonprice")
        new_image = request.FILES.get('image',None)
        site_obj = models.Site.objects.get(name=new_site)
        
        freightfee = request.POST.get("freightfee")
        tagpath = request.POST.get("tagpath")
        pageNow = "新增产品页"
        
        if new_sku =="" or new_childasin=="" or new_title=="" or new_description=="" or new_date=="":
            error_msg ="未完成表单必填内容"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        elif not new_image:
            error_msg ="未上传产品图片"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        else:
            sku_exist = models.ProductTemp.objects.filter(sku__contains =str(new_sku))
            if sku_exist:
                error_msg =new_sku+":sku重复,无法录入"
                addErrorlog(request,error_msg,pageNow)
                return render(request,'error.html',locals())
            else:
                if purchaseprice =="0.00" or weight=="0.000" or length=="0.00" or width=="0.00" or height=="0.00" or volumeweight=="0.000" or packagefee=="0.00"\
                    or opfee=="0.00" or fbafee=="0.00" or amazonfee=="0.00" or payserfee=="0.00" or adcost=="0.00" or amazonprice=="0.00":

                    product_obj = models.ProductTemp.objects.create(sku = new_sku,childAsin=new_childasin,title=new_title,\
                            description=new_description,creater=user_obj,c_time=new_date,site=site_obj,purchasePrice=purchaseprice,weight=weight,\
                            length=length,width=width,height=height,volumeWeight=volumeweight,packageFee=packagefee,opFee=opfee,\
                            currency=currency,fbaFullfillmentFee=fbafee,amazonReferralFee=amazonfee,payoneerServiceFee=payserfee,\
                            amazonSalePrice=amazonprice,adcost=adcost,image=new_image,freightFee=freightfee,tagpath=tagpath)
                    items = request.POST.getlist('item')
                    itemamounts = request.POST.getlist('itemamount')

                    for item,itemamount in zip(items,itemamounts):
                        if item==u'' or itemamount==u'':
                            pass
                        else:
                            item_str=filter(str.isdigit,item.encode("utf-8"))
                            item_id = int(item_str)
                            item_amount_str=filter(str.isdigit,itemamount.encode("utf-8"))
                            item_amount = int(item_amount_str)
                            # 根据返回的物料id ,找出对应的物料对象
                            material_obj = models.InventoryMaterial.objects.get(id=item_id)
                            # 创建产品物料的多对多关系对象
                            pmrelation_obj = models.ProductMaterial.objects.create(pmMaterial=material_obj,pmProduct=product_obj,pmAmount=item_amount)
                    error_msg = "产品已创建,因备选内容不完整,故无法产生公式项"
                    return render(request,'error.html',locals())
                else:
                    if not freightfee or freightfee == 0 or str(freightfee) == "0.00":
                        _dhlfee = calDHLShippingFee(weight,length,width,height)
                        _shrinkage = calShrinkage(purchaseprice,_dhlfee,packagefee,opfee,currency,fbafee,adcost)
                        _margin,_marginRate = calMargin(purchaseprice,_dhlfee,packagefee,opfee,currency,fbafee,_shrinkage,adcost,amazonfee,payserfee,amazonprice)
                        _productCostP = calProductCostPercentage(purchaseprice,amazonprice,currency)
                        product_obj = models.ProductTemp.objects.create(sku = new_sku,childAsin=new_childasin,title=new_title,\
                                description=new_description,creater=user_obj,c_time=new_date,site=site_obj,purchasePrice=purchaseprice,weight=weight,\
                                length=length,width=width,height=height,volumeWeight=volumeweight,packageFee=packagefee,opFee=opfee,\
                                currency=currency,fbaFullfillmentFee=fbafee,amazonReferralFee=amazonfee,payoneerServiceFee=payserfee,\
                                amazonSalePrice=amazonprice,adcost=adcost,image=new_image,dhlShippingFee=_dhlfee,shrinkage=_shrinkage,\
                                margin=_margin,marginRate=_marginRate,productCostPercentage=_productCostP,tagpath=tagpath)
                    else:
                        _dhlfee = calDHLShippingFee(weight,length,width,height)
                        _shrinkage = calShrinkage(purchaseprice,freightfee,packagefee,opfee,currency,fbafee,adcost)
                        _margin,_marginRate = calMargin(purchaseprice,freightfee,packagefee,opfee,currency,fbafee,_shrinkage,adcost,amazonfee,payserfee,amazonprice)
                        _productCostP = calProductCostPercentage(purchaseprice,amazonprice,currency)
                        product_obj = models.ProductTemp.objects.create(sku = new_sku,childAsin=new_childasin,title=new_title,\
                                description=new_description,creater=user_obj,c_time=new_date,site=site_obj,purchasePrice=purchaseprice,weight=weight,\
                                length=length,width=width,height=height,volumeWeight=volumeweight,packageFee=packagefee,opFee=opfee,\
                                currency=currency,fbaFullfillmentFee=fbafee,amazonReferralFee=amazonfee,payoneerServiceFee=payserfee,\
                                amazonSalePrice=amazonprice,adcost=adcost,image=new_image,dhlShippingFee=_dhlfee,shrinkage=_shrinkage,\
                                margin=_margin,marginRate=_marginRate,productCostPercentage=_productCostP,freightFee=freightfee,tagpath=tagpath)
                    items = request.POST.getlist('item')
                    itemamounts = request.POST.getlist('itemamount')

                    for item,itemamount in zip(items,itemamounts):
                        if item==u'' or itemamount==u'':
                            pass
                        else:
                            item_str=filter(str.isdigit,item.encode("utf-8"))
                            item_id = int(item_str)
                            item_amount_str=filter(str.isdigit,itemamount.encode("utf-8"))
                            item_amount = int(item_amount_str)
                            # 根据返回的物料id ,找出对应的物料对象
                            material_obj = models.InventoryMaterial.objects.get(id=item_id)
                            # 创建产品物料的多对多关系对象
                            pmrelation_obj = models.ProductMaterial.objects.create(pmMaterial=material_obj,pmProduct=product_obj,pmAmount=item_amount)
                    _act = "新建产品"+new_sku
                    models.AutoLog.objects.create(date=getTime(),user=user_obj,act=_act)
                    return HttpResponse("已创建完整产品信息")
                    


def productDetail(request,id):
    # 判断是否登录
    if not request.session.get('is_login',None):
        return redirect('/index')
    try:
        # print id
        producttemp = models.ProductTemp.objects.get(id=id)
        productindex = models.ProductMaterial.objects.filter(pmProduct=producttemp)
    except:
        pass
    return render(request, 'productdetail.html', locals())

def outStock(request):
    if not request.session.get('is_login',None):
        return redirect('/index')
    
    outstocks = models.OutStock.objects.all().order_by('-id')
    return render(request,'outstock.html',locals())

def outStockDetail(request,id):
    if not request.session.get('is_login',None):
        return redirect('/index')
    try:
        #通过outstock的id找出对象
        outstock = models.OutStock.objects.get(id=id)
        #1对多的对象
        outitems = models.OutItem.objects.filter(master=id)
    except:
        pass

    return render(request,'outstockdetail.html',locals())

class Outstockadd(View):
    #检查登录,提供user的下拉对象,渲染
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写表单并选择产品"
        #users用来制作下拉菜单
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        return render(request,'outstockadd.html',locals())
    
    #获取表单对象,对表单数据进行净化判断,对出库对象进行处理
    def post(self,request):
        new_code = request.POST.get('code')
        new_c_time = request.POST.get('c_time')
        new_description = request.POST.get('description')
        
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        pageNow = "新增出库"
        #检查空值
        if new_code == "" or new_c_time == "" or new_description == "":
            error_msg ="未完整填写表单"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        else:
            code_exist = models.OutStock.objects.filter(code = str(new_code))
            if code_exist:
                error_msg =new_code+":出库编号重复"
                addErrorlog(request,error_msg,pageNow)
                return render(request,'error.html',locals())
                
            # 创建outstock对象,修改物料数量
            else:

                outstock_obj = models.OutStock.objects.create(code=new_code,c_time=new_c_time,description=new_description,userOutstock=user_obj)
                items = request.POST.getlist('item')
                itemamounts = request.POST.getlist("itemamount")
                
                for item,itemamount in zip(items,itemamounts):
                    if item == u'' or itemamount == u'':
                        pass
                    else:
                        item_id = int(item)
                        item_amount = int(itemamount)
                        product_obj = models.ProductTemp.objects.get(id=item_id)
                        _site = str(product_obj.site.name)

                        product_index = models.ProductMaterial.objects.filter(pmProduct=product_obj)
                        #每一个product对应了多个物料,和数量,遍历这些参数,便于增减
                        for index in product_index:
                            material_obj = index.pmMaterial
                            #将产品数量*对应物料的消耗个数
                            if material_obj.amount < index.pmAmount*item_amount:
                                error_msg =material_obj.uniqueId+":库存不足,无法出库"
                                addErrorlog(request,error_msg,pageNow)
                                return render(request,'error.html',locals())
                            else:
                                material_obj.amount -= index.pmAmount*item_amount
                                material_obj.save()
                        if product_obj.dhlShippingFee :
                            
                            _dhlfee = product_obj.dhlShippingFee
                            _totalfee = _dhlfee*item_amount
                            item_object = models.OutItem.objects.create(master=outstock_obj,productName=product_obj,amountOut=item_amount,\
                                      dhlshippingfeeInput=_dhlfee,totalfee=_totalfee,siteinput=_site)
                        else:
                            item_object = models.OutItem.objects.create(master=outstock_obj,productName=product_obj,amountOut=item_amount,siteinput=_site)

                message = "已完成出库,请查看出库详情页"
                _act = "新增出库"+new_code
                models.AutoLog.objects.create(date=getTime(),user=user_obj,act=_act)
                return render(request,'outstockadd.html',locals())


def outItem(request):
    producttemps = models.ProductTemp.objects.all()
    return render(request,'outitem.html',locals())

def preOutItem(request):
    producttemps = models.ProductTemp.objects.all()
    return render(request,'preoutitem.html',locals())


class Uploadoutstock(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写表单并选择上传文件"
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        date = getTime()
        lastcode = models.OutStock.objects.all().order_by('-id')[0].code
        return render(request,'uploadoutstock.html',locals())
    
    def post(self,request):
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        new_c_time = request.POST.get('c_time')
        new_code = request.POST.get('code')
        new_description = request.POST.get('description')
        File = request.FILES.get('files',None)
        pageNow = "批量出库页"
        if File is None or new_code == "":
            error_msg ="未完整填写表单"
            return render(request,'error.html',locals())
        else:
            # 对code查重
            code_exist = models.OutStock.objects.filter(code = str(new_code))
            if code_exist:
                error_msg =new_code+":出库编号重复"
                addErrorlog(request,error_msg,pageNow)
                return render(request,'error.html',locals())
                
            else:
                #这里先建立outstock对象,再逐个产品创建outitem对象

                outstock_obj = models.OutStock.objects.create(code=new_code,c_time=new_c_time,description=new_description,userOutstock=user_obj)
                
                type_excel = File.name.split('.')[-1]
                if 'xlsx'== type_excel:
                    
                    upload_obj = models.Uploadfiles.objects.create(uploaduser=user_obj,date=new_c_time,file_name=File.name)
                    wb = xlrd.open_workbook(filename=None,file_contents=File.read())
                    table = wb.sheets()[0]
                    nrows = table.nrows
                    rowValue0 = table.row_values(0)
                    tag = rowValue0[0]
                    if tag != "outstocktable":
                        outstock_obj.delete()
                        error_msg =str(File.name)+":未识别到批量出库excel模板"
                        addErrorlog(request,error_msg,pageNow)
                        return render(request,'error.html',locals())
                    else:
                        pass
                        
                    error_tag = 0
                    sumfreightfee = 0
                    
                    try:
                        with transaction.atomic():
                            for i in range(2,nrows):
                                rowValues = table.row_values(i)
                                _sku = rowValues[1]
                                amountout,amount_tag = judgeint(rowValues[2])
                                pt_test = models.ProductTemp.objects.filter(sku=_sku)
                                
                                if pt_test and amount_tag:
                                    product_obj = models.ProductTemp.objects.get(sku=_sku)
                                    product_index = models.ProductMaterial.objects.filter(pmProduct=product_obj)
                                    for index in product_index:
                                        material_obj = index.pmMaterial
                                        if material_obj.amount < index.pmAmount*amountout:
                                            error_msg = material_obj.uniqueId+":库存不足,无法出库"
                                            addErrorlog(request,error_msg,pageNow)
                                            error_tag = 1
                                            break
                                        else:
                                            material_obj.amount -= index.pmAmount*amountout
                                            material_obj.save()
                                    #对一种产品的循环完成后,对该产品的出库创建对象
                                    _dhlfee,tag_dhl = judgeint(rowValues[3])
                                    _totalfee = _dhlfee*amountout
                                    sumfreightfee += _totalfee
                                    models.OutItem.objects.create(master=outstock_obj,productName=product_obj,amountOut=amountout,\
                                        site=rowValues[0],freightfee=_totalfee)
                                elif not amount_tag:
                                    error_msg = "sku:"+_sku+"数量有误,请检查"
                                    addErrorlog(request,error_msg,pageNow)
                                    error_tag = 1
                                else:
                                    error_msg = "sku:"+_sku+"   该产品尚未创建,无法出库"
                                    addErrorlog(request,error_msg,pageNow)
                                    error_tag = 1
                            if error_tag == 0:
                                message = "上传完成"
                            else:
                                message = "上传完成,请查看错误日志"
                            outstock_obj.total_freightfee = sumfreightfee
                            outstock_obj.save()
                            _act = "批量出库"+new_code
                            models.AutoLog.objects.create(date=getTime(),user=user_obj,act=_act)
                            return render(request,'uploadoutstock.html',locals())
                    except Exception as e:
                        error_msg ="出现未定义错误,未完成上传"
                        addErrorlog(request,error_msg,pageNow)
                        return render(request,'error.html',locals())
                else:
                    error_msg =str(File.name)+":上传文件格式不是xlsx"
                    addErrorlog(request,error_msg,pageNow)
                    return render(request,'error.html',locals())

def searchtest(request):
    return render(request,"searchtest.html")

class Uploadnewpro(View):
    
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写表单并选择上传文件"
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        date = getTime()
        return render(request,'uploadnewpro.html',locals())

    def post(self,request):

        new_c_time = request.POST.get('c_time')
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        File = request.FILES.get('files',None)
        pageNow = "批量新增产品页"
        if File is None or new_c_time == "" :
            error_msg ="未完整填写表单"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        else:
            type_excel = File.name.split('.')[-1]
            if 'xlsx'== type_excel:
                upload_obj = models.Uploadfiles.objects.create(uploaduser=user_obj,date=new_c_time,file_name=File.name)
                wb = xlrd.open_workbook(filename=None,file_contents=File.read())
                table = wb.sheets()[0]
                nrows = table.nrows
                ncols = table.ncols
                #识别模板
                rowValue0 = table.row_values(0)
                tag = rowValue0[0]
                if tag != "newprotable":
                    error_msg =str(File.name)+"未识别到新建产品excel模板"
                    addErrorlog(request,error_msg,pageNow)
                    return render(request,'error.html',locals())
                else:
                    pass
                
                #原子化
                # try:
                    # with transaction.atomic():
                error_tag = 0
                for i in range(2,nrows):
                    rowValues = table.row_values(i)
                    
                    new_sku = rowValues[1]
                    new_childasin = rowValues[2]
                    new_title = rowValues[3]
                    new_site = rowValues[0]
                    
                    if new_sku=="" or new_childasin=="" or new_title=="" or new_site=="":
                        error_msg = str(File.name)+"第"+str(i+1)+"行的必填项目不完整,请检查."
                        addErrorlog(request,error_msg,pageNow)
                        error_tag = 1
                        # return render(request,'error.html',locals())
                    else:
                        site_exist = models.Site.objects.filter(name=new_site)
                        sku_exist = models.ProductTemp.objects.filter(sku=new_sku)
                        new_description = rowValues[24]
                        #标签路径
                        if rowValues[26] == "":
                            tagpath = "C:\\"
                        else:
                            tagpath = rowValues[26]
                        
                        #实际运费
                        if rowValues[25] == "":
                            freightfee = 0
                        else:
                            freightfee,f_tag = judgeinput(rowValues[25])
                        
                        if not sku_exist and site_exist :
                            site_obj = models.Site.objects.get(name=new_site)
                            tagE = 1#判断是否有空项
                            list_col = [4,5,6,7,8,9,11,12,13,14,16,17,18,19]

                            dic_items = collections.OrderedDict([("purchaseprice","0.00"),("weight","0.000"),("length","0.00"),("width","0.00"),\
                                    ("height","0.00"),("volumeweight","0.000"),("packagefee","0.00"),("opfee","0.00"),("currency","6.50000"),\
                                    ("fbafee","0.00"),("adcost","0.00"),("amazonfee","0.00"),("payserfee","0.00"),("amazonprice","0.00")])
                            for col,item in zip(list_col,dic_items):
                                if rowValues[col] == "":
                                    tagE = 0
                                else:
                                    dic_items[item]=rowValues[col]
                            
                            if tagE == 0 and freightfee == 0:
                                product_obj = models.ProductTemp.objects.create(sku = new_sku,childAsin=new_childasin,title=new_title,\
                                    description=new_description,creater=user_obj,c_time=new_c_time,site=site_obj,purchasePrice=dic_items["purchaseprice"],weight=dic_items["weight"],\
                                    length=dic_items["length"],width=dic_items["width"],height=dic_items["height"],volumeWeight=dic_items["volumeweight"],packageFee=dic_items["packagefee"],opFee=dic_items["opfee"],\
                                    currency=dic_items["currency"],fbaFullfillmentFee=dic_items["fbafee"],amazonReferralFee=dic_items["amazonfee"],payoneerServiceFee=dic_items["payserfee"],\
                                    amazonSalePrice=dic_items["amazonprice"],adcost=dic_items["adcost"],tagpath = tagpath,freightFee=freightfee)
                                print "pt_obj created"
                                for j in range(27,ncols,2):
                                    material_exist = models.InventoryMaterial.objects.filter(uniqueId=rowValues[j])
                                    if rowValues[j]=="":
                                        if j==27:
                                            error_msg = "第"+str(i+1)+"行未识别到物料"
                                            addErrorlog(request,error_msg,pageNow)
                                        else:
                                            pass
                                        break
                                    elif material_exist:
                                        material_obj = models.InventoryMaterial.objects.get(uniqueId=rowValues[j])
                                        material_amount,mat_tag = judgeint(rowValues[j+1])
                                        pmrelation_obj = models.ProductMaterial.objects.create(pmMaterial=material_obj,pmProduct=product_obj,pmAmount=material_amount)
                                        if not mat_tag:
                                            error_msg = "第"+str(i+1)+"行物料uniqueID:   "+str(rowValues[j])+"   数量有误,请检查数据."
                                            addErrorlog(request,error_msg,pageNow)
                                            error_tag = 1
                                    else :
                                        error_msg = "第"+str(i+1)+"行物料uniqueID:   "+str(rowValues[j])+"   未查询到,请检查数据."
                                        addErrorlog(request,error_msg,pageNow)
                                        error_tag = 1
                                        
                                        # return render(request,'error.html',locals())
                            else:
                                #这里要计算那堆乱七八糟了.tagE =1
                                if not freightfee or freightfee == 0 :
                                    _dhlfee = calDHLShippingFee(dic_items["weight"],dic_items["length"],dic_items["width"],dic_items["height"])
                                    _shrinkage = calShrinkage(dic_items["purchaseprice"],_dhlfee,dic_items["packagefee"],dic_items["opfee"],dic_items["currency"],dic_items["fbafee"],dic_items["adcost"])
                                    _margin,_marginRate = calMargin(dic_items["purchaseprice"],_dhlfee,dic_items["packagefee"],dic_items["opfee"],\
                                        dic_items["currency"],dic_items["fbafee"],_shrinkage,dic_items["adcost"],dic_items["amazonfee"],dic_items["payserfee"],dic_items["amazonprice"])
                                    _productCostP = calProductCostPercentage(dic_items["purchaseprice"],dic_items["amazonprice"],dic_items["currency"])
                                    product_obj = models.ProductTemp.objects.create(sku = new_sku,childAsin=new_childasin,title=new_title,\
                                        description=new_description,creater=user_obj,c_time=new_c_time,site=site_obj,purchasePrice=dic_items["purchaseprice"],weight=dic_items["weight"],\
                                        length=dic_items["length"],width=dic_items["width"],height=dic_items["height"],volumeWeight=dic_items["volumeweight"],packageFee=dic_items["packagefee"],opFee=dic_items["opfee"],\
                                        currency=dic_items["currency"],fbaFullfillmentFee=dic_items["fbafee"],amazonReferralFee=dic_items["amazonfee"],payoneerServiceFee=dic_items["payserfee"],\
                                        amazonSalePrice=dic_items["amazonprice"],adcost=dic_items["adcost"],dhlShippingFee=_dhlfee,shrinkage=_shrinkage,\
                                        margin=_margin,marginRate=_marginRate,productCostPercentage=_productCostP,tagpath = tagpath,freightFee=freightfee)
                                else:
                                    _dhlfee = calDHLShippingFee(dic_items["weight"],dic_items["length"],dic_items["width"],dic_items["height"])
                                    _shrinkage = calShrinkage(dic_items["purchaseprice"],freightfee,dic_items["packagefee"],dic_items["opfee"],dic_items["currency"],dic_items["fbafee"],dic_items["adcost"])
                                    _margin,_marginRate = calMargin(dic_items["purchaseprice"],freightfee,dic_items["packagefee"],dic_items["opfee"],\
                                        dic_items["currency"],dic_items["fbafee"],_shrinkage,dic_items["adcost"],dic_items["amazonfee"],dic_items["payserfee"],dic_items["amazonprice"])
                                    _productCostP = calProductCostPercentage(dic_items["purchaseprice"],dic_items["amazonprice"],dic_items["currency"])
                                    product_obj = models.ProductTemp.objects.create(sku = new_sku,childAsin=new_childasin,title=new_title,\
                                        description=new_description,creater=user_obj,c_time=new_c_time,site=site_obj,purchasePrice=dic_items["purchaseprice"],weight=dic_items["weight"],\
                                        length=dic_items["length"],width=dic_items["width"],height=dic_items["height"],volumeWeight=dic_items["volumeweight"],packageFee=dic_items["packagefee"],opFee=dic_items["opfee"],\
                                        currency=dic_items["currency"],fbaFullfillmentFee=dic_items["fbafee"],amazonReferralFee=dic_items["amazonfee"],payoneerServiceFee=dic_items["payserfee"],\
                                        amazonSalePrice=dic_items["amazonprice"],adcost=dic_items["adcost"],dhlShippingFee=_dhlfee,shrinkage=_shrinkage,\
                                        margin=_margin,marginRate=_marginRate,productCostPercentage=_productCostP,tagpath = tagpath,freightFee=freightfee)
                                print "pt_obj created"
                                for j in range(27,ncols,2):
                                    material_exist = models.InventoryMaterial.objects.filter(uniqueId=rowValues[j])
                                    if rowValues[j]=="":
                                        if j==27:
                                            error_msg = "第"+str(i+1)+"行未识别到物料"
                                            addErrorlog(request,error_msg,pageNow)
                                        else:
                                            pass
                                        break
                                    elif material_exist:
                                        material_obj = models.InventoryMaterial.objects.get(uniqueId=rowValues[j])
                                        material_amount,mat_tag = judgeint(rowValues[j+1])
                                        pmrelation_obj = models.ProductMaterial.objects.create(pmMaterial=material_obj,pmProduct=product_obj,pmAmount=material_amount)
                                        if not mat_tag:
                                            error_msg = "第"+str(i+1)+"行物料uniqueID:   "+str(rowValues[j])+"   数量有误,请检查数据."
                                            addErrorlog(request,error_msg,pageNow)
                                            error_tag = 1
                                    else :
                                        error_msg = "第"+str(i+1)+"行物料uniqueID:   "+str(rowValues[j])+"   未查询到,请检查数据."
                                        addErrorlog(request,error_msg,pageNow)
                                        error_tag = 1
                        else:
                            error_msg = "第"+str(i+1)+"行站点名称未注册 或 sku重复."
                            addErrorlog(request,error_msg,pageNow)
                            error_tag = 1
                            # return render(request,'error.html',locals())
                if error_tag == 0:
                    message = "上传完毕,请在产品表查看并核对"
                else:
                    message = "上传完毕,请在错误日志查看出错信息"
                _act = "批量新增产品"
                models.AutoLog.objects.create(date=getTime(),user=user_obj,act=_act)
                return render(request,'uploadnewpro.html',locals())
                # except Exception as e:
                    # error_msg = str(File.name)+":出现未定义错误,未完成上传"
                    # addErrorlog(request,error_msg,pageNow)
                    # return render(request,'error.html',locals())
            else:
                error_msg =str(File.name)+":上传文件格式不是xlsx"
                addErrorlog(request,error_msg,pageNow)
                return render(request,'error.html',locals())


class Changecurrency(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写表单"
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        sites = models.Site.objects.all()
        return render(request,'changecurrency.html',locals())
    
    def post(self,request):
        pageNow = "修改汇率页"
        new_currency = request.POST.get('currency')
        new_currency,_tag = judgeinput(new_currency)
        site = request.POST.get('site')

        if new_currency == "":
            error_msg = "未正确输入汇率"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        else:
            product_objs = models.ProductTemp.objects.filter(site__name=site)
            if not product_objs:
                error_msg =site+":该站点下没有产品"
                addErrorlog(request,error_msg,pageNow)
                return render(request,'error.html',locals())
            
            else:
                for product_obj in product_objs:
                    if product_obj.dhlShippingFee == 0 and product_obj.freightFee == 0:
                        product_obj.currency = new_currency
                        product_obj.save()
                    elif (product_obj.dhlShippingFee != 0) and (product_obj.freightFee == 0):
                        _shrinkage = calShrinkage(product_obj.purchasePrice,product_obj.dhlShippingFee,product_obj.packageFee,product_obj.opFee,new_currency,product_obj.fbaFullfillmentFee,product_obj.adcost)
                        _margin,_marginRate = calMargin(product_obj.purchasePrice,product_obj.dhlShippingFee,product_obj.packageFee,product_obj.opFee,\
                                            new_currency,product_obj.fbaFullfillmentFee,_shrinkage,product_obj.adcost,product_obj.amazonReferralFee,product_obj.payoneerServiceFee,product_obj.amazonSalePrice)
                        _productCostP = calProductCostPercentage(product_obj.purchasePrice,product_obj.amazonSalePrice,new_currency) 
                        models.ProductTemp.objects.filter(id=product_obj.id).update(shrinkage=_shrinkage,margin=_margin,marginRate=_marginRate,productCostPercentage=_productCostP,currency=new_currency)
                    elif product_obj.freightFee != 0:
                        _shrinkage = calShrinkage(product_obj.purchasePrice,product_obj.freightFee,product_obj.packageFee,product_obj.opFee,new_currency,product_obj.fbaFullfillmentFee,product_obj.adcost)
                        _margin,_marginRate = calMargin(product_obj.purchasePrice,product_obj.freightFee,product_obj.packageFee,product_obj.opFee,\
                                            new_currency,product_obj.fbaFullfillmentFee,_shrinkage,product_obj.adcost,product_obj.amazonReferralFee,product_obj.payoneerServiceFee,product_obj.amazonSalePrice)
                        _productCostP = calProductCostPercentage(product_obj.purchasePrice,product_obj.amazonSalePrice,new_currency)
                        models.ProductTemp.objects.filter(id=product_obj.id).update(shrinkage=_shrinkage,margin=_margin,marginRate=_marginRate,productCostPercentage=_productCostP,currency=new_currency)
                    
        message = "更新完毕,请在产品表核查结果."
        _act = "修改汇率"+site
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        models.AutoLog.objects.create(date=getTime(),user=user_obj,act=_act)
        return render(request,'changecurrency.html',locals())


def error(request):
    error_msg = "没有发现错误"
    return render(request,'error.html',locals())


class ErrorLogList(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
            
        errorlogs = models.ErrorLog.objects.all().order_by('-id')
        q = request.GET.get('q','') #检索内容
        
        #检索部分的选择
        #这里对检索内容后面加了一个按id倒序
        if q:
            errorlogs = errorlogs.filter(Q(date__icontains=q) | Q(message__icontains=q) | Q(page__icontains=q))
        else:
            pass
            
        #分页部分
        paginator = Paginator(errorlogs,10)
        try:
            current_num = int(request.GET.get('page',1))
            errorlogs = paginator.page(current_num)
        except EmptyPage:
            errorlogs = paginator.page(1)
        if paginator.num_pages > 11:
            if current_num -5 <1:
                pageRange =range(1,11)
            elif current_num + 5>paginator.num_pages:
                pageRange = range(current_num-5,current_num+1)
            else:
                pageRange = range(current_num-5,current_num+6)
        else:
            pageRange = range(1,paginator.num_pages+1)
        return render(request,'errorloglist.html',locals())

def addErrorlog(request,message,page):
    user = request.session.get('user_name','None')
    user_obj = models.User.objects.get(name = user)
    errorlog_obj = models.ErrorLog.objects.create(user=user_obj,date=getTime(),message=message,page=page)

#上传excel批量修改物料表
class Uploadmatmodify(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请选择上传文件"
        user = request.session.get('user_name','None')
        date=getTime()
        return render(request,'uploadmatmodify.html',locals())
    
    def post(self,request):
        new_c_time = request.POST.get('c_time')
        File = request.FILES.get('files',None)
        user = request.session.get('user_name','None')
        pageNow = "批量修改物料页"
        
        if File is None:
            error_msg = "未选择上传文件"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        else:
            #记录自动日志
            _act = "批量修改物料:"+File.name
            user_obj = models.User.objects.get(name=user)
            models.AutoLog.objects.create(date=new_c_time,user=user_obj,act=_act)
            
            type_excel = File.name.split('.')[-1] 
            if 'xlsx'== type_excel:
                #创建批量上传对象的记录
                upload_obj = models.Uploadfiles.objects.create(uploaduser=user,date=new_c_time,file_name=File.name)
                
                #excel数据操作
                wb = xlrd.open_workbook(filename=None,file_contents=File.read())
                table = wb.sheets()[0]
                nrows = table.nrows
                rowValue0 = table.row_values(0)
                tag = rowValue0[0]
                if tag != "uploadmaterialmodify":
                    error_msg =str(File.name)+":未识别到批量修改物料excel标准模板"
                    addErrorlog(request,error_msg,pageNow)
                    return render(request,'error.html',locals())
                else:
                    pass
                
                #原子化
                error_tag = 0
                for i in range(2,nrows):
                    rowValues = table.row_values(i)
                    uniq = rowValues[0]
                    new_description = rowValues[1]
                    new_amount = rowValues[2]
                    #判断是否存在user对象
                    user = rowValues[3]
                    if user:
                        purchaseuser = models.User.objects.filter(name=user)
                    else:
                        purchaseuser = None
                    price = rowValues[4]
                    price,tag = judgeinput(price)
                    
                    #首先查找有没有对应的uniqID
                    uniq_obj = models.InventoryMaterial.objects.filter(uniqueId=uniq)
                    if uniq and uniq_obj:
                        #判断excel中有哪些数据,有的就更新
                        #非空pass是ok的,不符合类型的pass还需要修改
                        if new_description:
                            uniq_obj.update(description=new_description)
                        else:
                            pass
                        if new_amount and isinstance(new_amount,int):
                            amount = abs(new_amount)
                            uniq_obj.update(amount=amount)
                        else:
                            pass
                        if purchaseuser:
                            new_user = purchaseuser[0]
                            uniq_obj.update(userPurchase=new_user)
                        else:
                            pass
                        if tag == "float":
                            ubiq_obj.update(price=price)
                        else:
                            pass
                        print "第"+str(i+1)+"行更新完毕"
                    else:
                        #这里后面会升级为整体报错模式
                        error_msg = "第"+str(i+1)+"行,sku在库存表中未查询到"
                        addErrorlog(request,error_msg,pageNow)
                        error_tag = 1
                        # return render(request,'error.html',locals())
                if error_tag == 0:
                    message = "已完成上传,请在物料库存表中核对"
                else:
                    message = "已完成上传,存在错误,请查看错误日志"
                return render(request,'uploadmatmodify.html',locals())

            else:
                error_msg = File.name+":上传文件格式不是xlsx"
                addErrorlog(request,error_msg,pageNow)
                return render(request,'error.html',locals())

        
class Uploadpromodify(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请选择上传文件"
        user = request.session.get('user_name','None')
        # user_obj = models.User.objects.get(name=user)
        date=getTime()
        return render(request,'uploadpromodify.html',locals())
    
    def post(self,request):
        new_c_time = request.POST.get('c_time')
        File = request.FILES.get('files',None)
        user = request.session.get('user_name','None')
        pageNow = "批量修改产品页"
        
        if File is None:
            error_msg = "未选择上传文件"
            addErrorlog(request,error_msg,pageNow)
            return render(request,'error.html',locals())
        else:
            #记录自动日志
            _act = "批量修改产品:"+File.name
            user_obj = models.User.objects.get(name=user)
            models.AutoLog.objects.create(date=new_c_time,user=user_obj,act=_act)
            type_excel = File.name.split('.')[-1] 
            
            if 'xlsx'== type_excel:
                upload_obj = models.Uploadfiles.objects.create(uploaduser=user,date=new_c_time,file_name=File.name)
                
                #excel数据操作
                wb = xlrd.open_workbook(filename=None,file_contents=File.read())
                table = wb.sheets()[0]
                nrows = table.nrows
                ncols = table.ncols
                rowValue0 = table.row_values(0)
                tag = rowValue0[0]
                if tag != "uploadproductmodify":
                    error_msg =str(File.name)+":未识别到批量修改产品excel标准模板"
                    addErrorlog(request,error_msg,pageNow)
                    return render(request,'error.html',locals())
                else:
                    pass
                #未原子化
                for i in range(2,nrows):
                    rowValues = table.row_values(i)
                    sku = rowValues[1]
                    list_col_fund = [2,3,24,25,26]
                    list_col_advance = [4,5,6,7,8,9,11,12,13,14,16,17,18,19]
                    list_name_fund = ["childAsin","title","description","freightFee","tagpath"]
                    list_name_advance = ["purchasePrice","weight","length","width","height","volumeWeight","packageFee",\
                                    "opFee","currency","fbaFullfillmentFee","adcost","amazonReferralFee","payoneerServiceFee","amazonSalePrice"]
                    #先判断sku
                    product_objs = models.ProductTemp.objects.filter(sku=sku)
                    #未找到sku,回头升级为整体报错
                    if not product_objs:
                        error_msg ="第"+str(i)+"行"+sku+":产品库未识别到该sku"
                        addErrorlog(request,error_msg,pageNow)
                        return render(request,'error.html',locals())
                    else:
                        #update用变量代替字段名,update(**{attr:value})
                        #是否进行公式项计算标签
                        tag_formula = 0
                        #基础项目更新,不影响公式项
                        for order,attr in zip(list_col_fund,list_name_fund):
                            if rowValues[order] == "":
                                pass
                            else:
                                new_value = rowValues[order]
                                product_objs.update(**{attr:new_value})
                        print "base attr updated"
                        
                        #详情项更新,需要重新计算formula
                        for order,attr in zip(list_col_advance,list_name_advance):
                            if rowValues[order] == "":
                                pass
                            else:
                                tag_formula = 1
                                new_value = rowValues[order]
                                product_objs.update(**{attr:new_value})
                        print "advanced attr updated"
                        
                        product_obj = product_objs[0]
                        #分有实际运费和没有两种情况计算数据
                        if not product_obj.freightFee or product_obj.freightFee == 0 or str(product_obj.freightFee) == "0.00":
                            _dhlfee = calDHLShippingFee(product_obj.weight,product_obj.length,product_obj.width,product_obj.height)
                            _shrinkage = calShrinkage(product_obj.purchasePrice,_dhlfee,product_obj.packageFee,product_obj.opFee,product_obj.currency,product_obj.fbaFullfillmentFee,product_obj.adcost)
                            _margin,_marginRate = calMargin(product_obj.purchasePrice,_dhlfee,product_obj.packageFee,product_obj.opFee,\
                                                product_obj.currency,product_obj.fbaFullfillmentFee,_shrinkage,product_obj.adcost,product_obj.amazonReferralFee,product_obj.payoneerServiceFee,product_obj.amazonSalePrice)
                            _productCostP = calProductCostPercentage(product_obj.purchasePrice,product_obj.amazonSalePrice,product_obj.currency)
                        else:
                            _shrinkage = calShrinkage(product_obj.purchasePrice,product_obj.freightFee,product_obj.packageFee,product_obj.opFee,product_obj.currency,product_obj.fbaFullfillmentFee,product_obj.adcost)
                            _margin,_marginRate = calMargin(product_obj.purchasePrice,product_obj.freightFee,product_obj.packageFee,product_obj.opFee,\
                                                product_obj.currency,product_obj.fbaFullfillmentFee,_shrinkage,product_obj.adcost,product_obj.amazonReferralFee,product_obj.payoneerServiceFee,product_obj.amazonSalePrice)
                            _productCostP = calProductCostPercentage(product_obj.purchasePrice,product_obj.amazonSalePrice,product_obj.currency)
                        print str(i)+":formula updated"
                        
                        #对mp关系进行修改,先查出product_obj的id,然后反查pm,再把pm清空,最后更新pm关系
                        if not rowValues[27]:
                            pass
                        else:
                            #清空pm关系
                            pid = product_obj.id
                            mp_relations = models.ProductMaterial.objects.filter(pmProduct=pid)
                            mp_relations.delete()
                            #创建新关系
                            for j in range(27,ncols,2):
                                material_exist = models.InventoryMaterial.objects.filter(uniqueId=rowValues[j])
                                if material_exist:
                                    material_obj = models.InventoryMaterial.objects.get(uniqueId=rowValues[j])
                                    material_amount = abs(int(rowValues[j+1]))
                                    pmrelation_obj = models.ProductMaterial.objects.create(pmMaterial=material_obj,pmProduct=product_obj,pmAmount=material_amount)
                                elif rowValues[j]=="":
                                    break
                                else :
                                    error_msg = "第"+str(i)+"行物料uniqueID:   "+str(rowValues[j])+"   未查询到,请检查数据."
                                    addErrorlog(request,error_msg,pageNow)
                                    return render(request,'error.html',locals())
                            print str(i)+":pm updated"

                message = "已完成上传,请在产品表中核对."
                return render(request,'uploadpromodify.html',locals())

            else:
                error_msg = File.name+":上传文件格式不是xlsx"
                addErrorlog(request,error_msg,pageNow)
                return render(request,'error.html',locals())

class Rapidmatmodify(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
            
        inventorymaterials = models.InventoryMaterial.objects.all().order_by('id')
        sort = request.GET.get('sort','') #排序方式
        q = request.GET.get('q','') #检索内容
        total_amount_obj = models.InventoryMaterial.objects.values('amount').aggregate(num=Sum('amount'))#总库存
        total_amount = total_amount_obj['num']
        #检索部分的选择
        if q:
            inventorymaterials = inventorymaterials.filter(Q(uniqueId__icontains=q) | 
                Q(description__icontains=q) | Q(amount__icontains=q))
        else:
            pass
        #排序部分
        if sort:
            if sort == 'amountincrease':
                inventorymaterials = inventorymaterials.order_by('amount')
            if sort == 'amountdecrease':
                inventorymaterials = inventorymaterials.order_by('-amount')
            else:
                pass
        else:
            pass
            
        #分页部分
        paginator = Paginator(inventorymaterials,10)
        try:
            current_num = int(request.GET.get('page',1))
            inventorymaterials = paginator.page(current_num)
        except EmptyPage:
            inventorymaterials = paginator.page(1)
        if paginator.num_pages > 11:
            if current_num -5 <1:
                pageRange =range(1,11)
            elif current_num + 5>paginator.num_pages:
                pageRange = range(current_num-5,current_num+1)
            else:
                pageRange = range(current_num-5,current_num+6)
        else:
            pageRange = range(1,paginator.num_pages+1)
            
        return render(request,'rapidmatmodify.html',locals())
    
    def post(self,request):
        tag_in = request.POST.get("tag_in")
        get_price = request.POST.get("get_price")
        get_amount = request.POST.get("get_amount")
        im_id = request.POST.get("im_id")
        id = int(im_id)
        
        mat_obj = models.InventoryMaterial.objects.get(id=id)
        if tag_in == "m_amount":
            new_amount,tag_amount = judgeint(get_amount)
            if not tag_amount:
                ret = {"tag_out":"wrong_type"}
            else:
                mat_obj.amount = new_amount
                mat_obj.save()
                tag_out="Success"
                ret = {"new_amount":new_amount,"tag_out":tag_out}
        elif tag_in == "m_price":
            new_price,tag_out = judgeinput(get_price)
            if tag_out == "wrong_type":
                ret = {"tag_out":"wrong_type"}
            else:
                mat_obj.price = new_price
                mat_obj.save()
                ret = {"new_price":new_price,"tag_out":"Success"}
        else:
            ret = {"tag_out":"wrong_type"}
        return HttpResponse(json.dumps(ret))
        
        
        
        
        
        
        
        
        
        
        
        
        
class Rapidpromodify(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        producttemps = models.ProductTemp.objects.all().order_by('id')

        q = request.GET.get('q','') #检索内容
        order = request.GET.get('order','')
        specify = request.GET.get('specify','')
        print specify
        
        #检索部分的选择
        if q:
            producttemps = producttemps.filter(Q(title__icontains=q) | Q(sku__icontains=q) | Q(description__icontains=q))
        else:
            pass
            
        #排序部分
        if specify == "id":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "purchasePrice":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "dhlShippingFee":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "freightFee":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "amazonSalePrice":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "margin":
            producttemps = producttemps.order_by(orderspecify(order,specify))
        elif specify == "marginRate":
            producttemps = producttemps.order_by(orderspecify(order,specify))


        #分页部分
        paginator = Paginator(producttemps,10)
        try:
            current_num = int(request.GET.get('page',1))
            producttemps = paginator.page(current_num)
        except EmptyPage:
            producttemps = paginator.page(1)
        if paginator.num_pages > 11:
            if current_num -5 <1:
                pageRange =range(1,11)
            elif current_num + 5>paginator.num_pages:
                pageRange = range(current_num-5,current_num+1)
            else:
                pageRange = range(current_num-5,current_num+6)
        else:
            pageRange = range(1,paginator.num_pages+1)
        _act = "浏览产品快速修改页"+" 搜索: "+q
        user = request.session.get('user_name','None')
        user_obj = models.User.objects.get(name=user)
        models.AutoLog.objects.create(date=getTime(),user=user_obj,act=_act)
        return render(request,'rapidpromodify.html',locals())
    
    def post(self,request):
        tag_in = request.POST.get("tag_in")
        get_pprice = request.POST.get("get_pprice")
        get_fee = request.POST.get("get_fee")
        get_sale = request.POST.get("get_sale")
        p_id = request.POST.get("p_id")
        id = int(p_id)
        product_obj = models.ProductTemp.objects.get(id=id)
        #对于修改采购价,运费,亚马逊售价进行数据清洗和计算,通过ajax返回字典
        if tag_in == "pprice":
            new_pprice,tag_out = judgeinput(get_pprice)
            if tag_out == "wrong_type":
                ret = {"tag_out":"wrong_type"}
            else:
                if not product_obj.freightFee or product_obj.freightFee == 0 or str(product_obj.freightFee) == "0.00":
                    _shrinkage = calShrinkage(new_pprice,product_obj.dhlShippingFee,product_obj.packageFee,product_obj.opFee,product_obj.currency,product_obj.fbaFullfillmentFee,product_obj.adcost)
                    _margin,_marginRate = calMargin(new_pprice,product_obj.dhlShippingFee,product_obj.packageFee,product_obj.opFee,\
                                          product_obj.currency,product_obj.fbaFullfillmentFee,_shrinkage,product_obj.adcost,product_obj.amazonReferralFee,product_obj.payoneerServiceFee,product_obj.amazonSalePrice)
                    product_obj.shrinkage = _shrinkage
                    product_obj.margin = _margin
                    product_obj.marginRate = _marginRate
                else:
                    _shrinkage = calShrinkage(new_pprice,product_obj.freightFee,product_obj.packageFee,product_obj.opFee,product_obj.currency,product_obj.fbaFullfillmentFee,product_obj.adcost)
                    _margin,_marginRate = calMargin(new_pprice,product_obj.freightFee,product_obj.packageFee,product_obj.opFee,\
                                          product_obj.currency,product_obj.fbaFullfillmentFee,_shrinkage,product_obj.adcost,product_obj.amazonReferralFee,product_obj.payoneerServiceFee,product_obj.amazonSalePrice)
                    product_obj.shrinkage = _shrinkage
                    product_obj.margin = _margin
                    product_obj.marginRate = _marginRate
                product_obj.purchasePrice = new_pprice
                product_obj.save()
                _m = round(_margin,3)
                _mr = str(round(_marginRate,3))+"%"
                ret = {"new_pprice":new_pprice,"new_margin":_m,"new_marginrate":_mr,"tag_out":tag_out}
            
        elif tag_in == "freightfee":
            new_freightfee,tag_out = judgeinput(get_fee)
            if tag_out == "wrong_type" or new_freightfee == 0:
                ret = {"tag_out":"wrong_type"}
            else:
                _shrinkage = calShrinkage(product_obj.purchasePrice,new_freightfee,product_obj.packageFee,product_obj.opFee,product_obj.currency,product_obj.fbaFullfillmentFee,product_obj.adcost)
                _margin,_marginRate = calMargin(product_obj.purchasePrice,new_freightfee,product_obj.packageFee,product_obj.opFee,\
                                   product_obj.currency,product_obj.fbaFullfillmentFee,_shrinkage,product_obj.adcost,product_obj.amazonReferralFee,product_obj.payoneerServiceFee,product_obj.amazonSalePrice)
                product_obj.shrinkage = _shrinkage
                product_obj.margin = _margin
                product_obj.marginRate = _marginRate
                product_obj.freightFee = new_freightfee
                product_obj.save()
                _m = round(_margin,3)
                _mr = str(round(_marginRate,3))+"%"
                ret = {"new_freightfee":new_freightfee,"new_margin":_m,"new_marginrate":_mr,"tag_out":tag_out}
        elif tag_in == "amazonSP":
            new_amazonprice,tag_out = judgeinput(get_sale)
            if tag_out == "wrong_type" or new_amazonprice == 0:
                ret = {"tag_out":"wrong_type"}
            else:
                if not product_obj.freightFee or product_obj.freightFee == 0 or str(product_obj.freightFee) == "0.00":
                    _margin,_marginRate = calMargin(product_obj.purchasePrice,product_obj.dhlShippingFee,product_obj.packageFee,product_obj.opFee,\
                                          product_obj.currency,product_obj.fbaFullfillmentFee,product_obj.shrinkage,product_obj.adcost,product_obj.amazonReferralFee,product_obj.payoneerServiceFee,new_amazonprice)
                    product_obj.margin = _margin
                    product_obj.marginRate = _marginRate
                else:
                    _margin,_marginRate = calMargin(product_obj.purchasePrice,product_obj.freightFee,product_obj.packageFee,product_obj.opFee,\
                                          product_obj.currency,product_obj.fbaFullfillmentFee,product_obj.shrinkage,product_obj.adcost,product_obj.amazonReferralFee,product_obj.payoneerServiceFee,new_amazonprice)
                    product_obj.margin = _margin
                    product_obj.marginRate = _marginRate
                product_obj.amazonSalePrice = new_amazonprice
                product_obj.save()
                _m = round(_margin,3)
                _mr = str(round(_marginRate,3))+"%"
                ret = {"new_amazonprice":new_amazonprice,"new_margin":_m,"new_marginrate":_mr,"tag_out":tag_out}
        else:
            pass
        return HttpResponse(json.dumps(ret))

def judgeinput(num):
    try:
        ret = float(num)
        tag_out = "float"
    except:
        ret = 0
        tag_out = "wrong_type"
    return abs(ret),tag_out

def judgeint(num):
    try:
        ret = int(num)
        tag_out = True
    except:
        ret = 0
        tag_out = False
    return abs(ret),tag_out

def getWeight(weight):
    if weight:
        pass
    else:
        weight = 0
    return weight

def getVolume(l,w,h):
    if l and w and h:
        volume = (l*w*h)/1000000
    else:
        volume = 0
    return volume
        
def decimal2float(listobj):
    listout=[]
    for item in listobj:
        listout.append(float(item))
    return listout

def repeatCheck(listin):
    _list = listin
    if len(_list) != len(set(_list)):
        return "repeat"
    else:
        return "no repeat"
        
class PreOutstock(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请完成表单所有项目"
        user = request.session.get('user_name','None')
        date=getTime()
        lastcode = models.PreOutstock.objects.all().order_by('-id')[0].pcode     
        return render(request,'preoutstock.html',locals())
    def post(self,request):
        message="已点击保存"
        pcode = request.POST.get('precode')
        ptime = request.POST.get('c_time')
        pdescription = request.POST.get('description')
        user = request.POST.get('user')
        user_obj = models.User.objects.get(name=user)
        pageNow = "新建预出库"
        #获取新的preoutitem
        items = request.POST.getlist('item')
        repeat_tag =repeatCheck(items)
        itemamounts = request.POST.getlist("itemamount")
        #上传的容器
        weight_list = []
        volume_list = []
        fee_list = []
        site_list = []
        path_list = []
        
        if pcode == "" or pdescription == "" or (not items) or (not itemamounts):
            error_msg = "未完整填写表单"
            addErrorlog(request,error_msg,pageNow)
            ret={"tag_out":error_msg}
            return HttpResponse(json.dumps(ret))
        elif repeat_tag == "repeat":
            error_msg = "表单中有重复项,请仔细检查"
            addErrorlog(request,error_msg,pageNow)
            ret={"tag_out":error_msg}
            return HttpResponse(json.dumps(ret))
        else:
            exist_obj = models.PreOutstock.objects.filter(pcode = str(pcode))
            if exist_obj:
                print "exist"
                exist_obj.update(ptime=ptime,pdescription=pdescription,user=user_obj)
                preoutstock_obj = exist_obj[0]
                #写日志
                _act = "修改了预出库表:"+str(pcode)
                models.AutoLog.objects.create(date=ptime,user=user_obj,act=_act)

                #清空旧的preoutitem
                models.PreOutitem.objects.filter(master=preoutstock_obj).delete()
                #检查是否有空项

                for item,itemamount in zip(items,itemamounts):
                    item_amount,tag_sku = judgeint(itemamount)
                    sku_exist = models.ProductTemp.objects.filter(sku=item)
                    
                    if item == u'' or itemamount == u'':
                        error_msg = "预出库项中存在sku或数量漏填的项,请检查"
                        addErrorlog(request,error_msg,pageNow)
                        ret={"tag_out":error_msg}
                        return HttpResponse(json.dumps(ret))
                    elif (not tag_sku) or (not sku_exist):
                        error_msg = item+"的sku未检索到或其数量不是整数,请检查"
                        ret={"tag_out":error_msg}
                        return HttpResponse(json.dumps(ret))
                    else:
                        item=str(item)
                        product_obj = models.ProductTemp.objects.get(sku=item)
                        #创建多对多的对象
                        preitem_obj = models.PreOutitem.objects.create(master=preoutstock_obj,productName=product_obj,amount=item_amount)
                        #创建PreOutitem对象,获取其重量,体积,运费,便于计算整体数据.
                        item_weight = getWeight(product_obj.weight)
                        #函数判断,如果长宽高不全存在,就返回0
                        item_volume = getVolume(product_obj.length,product_obj.width,product_obj.height)
                        #如果存在实际运费,就他;如果不存在,而dhl存在,就dhl;都没有,就0
                        if product_obj.freightFee and product_obj.freightFee != 0:
                            item_freightfee = product_obj.freightFee
                        elif item_volume != 0 and product_obj.dhlShippingFee:
                            item_freightfee = product_obj.dhlShippingFee
                        else:
                            item_freightfee = 0 
                        item_weight_sum = item_weight*item_amount
                        item_volume_sum = item_volume*item_amount
                        item_freightfee_sum = item_freightfee*item_amount
                        site = product_obj.site.name
                        if product_obj.tagpath:
                            path = product_obj.tagpath
                        else:
                            path = "not define"
                        
                        weight_list.append(item_weight_sum)
                        volume_list.append(item_volume_sum)
                        fee_list.append(item_freightfee_sum)
                        site_list.append(site)
                        path_list.append(path)
                total_weight = float(sum(weight_list))
                total_volume = float(sum(volume_list))
                total_fee = float(sum(fee_list))
                
                fw_list = decimal2float(weight_list)
                fv_list = decimal2float(volume_list)
                ff_list = decimal2float(fee_list)
                
                preoutstock_obj.total_weight = total_weight
                preoutstock_obj.total_volume = total_volume
                preoutstock_obj.total_freightfee = total_fee
                preoutstock_obj.save()
                
                ret = {"total_weight":total_weight,"total_volume":total_volume,"total_fee":total_fee,"tag_out":"ok",\
                    "site_list":site_list,"weight_list":fw_list,"volume_list":fv_list,"fee_list":ff_list,"path_list":path_list}
                return HttpResponse(json.dumps(ret))
                
            else:
                preoutstock_obj = models.PreOutstock.objects.create(pcode=pcode,ptime=ptime,pdescription=pdescription,user=user_obj)
                #写日志
                _act = "创建了预出库表:"+str(pcode)
                models.AutoLog.objects.create(date=ptime,user=user_obj,act=_act)

                for item,itemamount in zip(items,itemamounts):
                    item_amount,tag_sku = judgeint(itemamount)
                    sku_exist = models.ProductTemp.objects.filter(sku=item)
                    if item == u'' or itemamount == u'' :
                        error_msg = "预出库项中存在sku或数量漏填的项,请检查"
                        addErrorlog(request,error_msg,pageNow)
                        ret={"tag_out":error_msg}
                        return HttpResponse(json.dumps(ret))
                    elif (not tag_sku) or (not sku_exist):
                        error_msg = item+"的sku未检索到或其数量不是整数,请检查"
                        ret={"tag_out":error_msg}
                        return HttpResponse(json.dumps(ret))
                    else:
                        item=str(item)
                        product_obj = models.ProductTemp.objects.get(sku=item)
                        #创建多对多的对象
                        preitem_obj = models.PreOutitem.objects.create(master=preoutstock_obj,productName=product_obj,amount=item_amount)
                        
                        #创建PreOutitem对象,获取其重量,体积,运费,便于计算整体数据.
                        item_weight = getWeight(product_obj.weight)
                        #函数判断,如果长宽高不全存在,就返回0
                        item_volume = getVolume(product_obj.length,product_obj.width,product_obj.height)
                        #如果存在实际运费,就他;如果不存在,而dhl存在,就dhl;都没有,就0
                        if product_obj.freightFee and product_obj.freightFee != 0:
                            item_freightfee = product_obj.freightFee
                        elif item_volume != 0 and product_obj.dhlShippingFee:
                            item_freightfee = product_obj.dhlShippingFee
                        else:
                            item_freightfee = 0 
                        item_weight_sum = item_weight*item_amount
                        item_volume_sum = item_volume*item_amount
                        item_freightfee_sum = item_freightfee*item_amount
                        site = product_obj.site.name
                        if product_obj.tagpath:
                            path = product_obj.tagpath
                        else:
                            path = "not define"
                        
                        weight_list.append(item_weight_sum)
                        volume_list.append(item_volume_sum)
                        fee_list.append(item_freightfee_sum)
                        site_list.append(site)
                        path_list.append(path)
                total_weight = float(sum(weight_list))
                total_volume = float(sum(volume_list))
                total_fee = float(sum(fee_list))
                
                fw_list = decimal2float(weight_list)
                fv_list = decimal2float(volume_list)
                ff_list = decimal2float(fee_list)
                
                preoutstock_obj.total_weight = total_weight
                preoutstock_obj.total_volume = total_volume
                preoutstock_obj.total_freightfee = total_fee
                preoutstock_obj.save()
                
                ret = {"total_weight":total_weight,"total_volume":total_volume,"total_fee":total_fee,"tag_out":"ok",\
                    "site_list":site_list,"weight_list":fw_list,"volume_list":fv_list,"fee_list":ff_list,"path_list":path_list}
                return HttpResponse(json.dumps(ret))

def pre2OutStock(request):
    #这里只要模仿出库页就可以了吧
    pcode = request.POST.get('precode')
    new_c_time = getTime()
    new_description = request.POST.get('description')
    new_code = request.POST.get("get_code")
    user = request.POST.get("user")
    user_obj = models.User.objects.get(name=user)
    pageNow = "从预出库页新增出库"
    #上传的容器
    weight_list = []
    volume_list = []
    fee_list = []

    #检查空值
    if new_code == "" or new_c_time == "" or new_description == "":
        #报错日志记录
        error_msg ="未完整填写表单"
        addErrorlog(request,error_msg,pageNow)
        #前端报错
        tag_out = "Error:"+error_msg
        ret = {"tag_out":tag_out}
        return HttpResponse(json.dumps(ret))
    else:
        code_exist = models.OutStock.objects.filter(code = str(new_code))
        if code_exist:
            #报错日志记录
            error_msg =new_code+":出库编号重复"
            addErrorlog(request,error_msg,pageNow)
            #前端报错
            tag_out = "Error:"+error_msg
            ret = {"tag_out":tag_out}
            return HttpResponse(json.dumps(ret))
        else:
            outstock_obj = models.OutStock.objects.create(code=new_code,c_time=new_c_time,description=new_description,userOutstock=user_obj)
            items = request.POST.getlist('item')
            repeat_tag =repeatCheck(items)
            itemamounts = request.POST.getlist("itemamount")
            
            #整体报错体系还需要思考
            for item,itemamount in zip(items,itemamounts):
                item_amount,itemtag_out = judgeint(itemamount)
                sku_exist = models.ProductTemp.objects.filter(sku=item)

                if item == u'' or itemamount == u'':
                    error_msg = "预出库项中存在sku或数量漏填的项,请检查"
                    addErrorlog(request,error_msg,pageNow)
                    ret={"tag_out":error_msg}
                    return HttpResponse(json.dumps(ret))
                elif repeat_tag == "repeat":
                    error_msg = "表单中有重复项,请仔细检查"
                    addErrorlog(request,error_msg,pageNow)
                    ret={"tag_out":error_msg}
                    return HttpResponse(json.dumps(ret))
                elif (not itemtag_out) or (not sku_exist):
                    error_msg = item+"的sku未检索到或其数量不是整数,请检查"
                    ret={"tag_out":error_msg}
                    return HttpResponse(json.dumps(ret))
                else:
                    item=str(item)
                    #拿到循环中需要的产品对象
                    product_obj = models.ProductTemp.objects.get(sku=item)
                    _site = str(product_obj.site.name)
                    #拿到产品对应的物料对象set
                    product_index = models.ProductMaterial.objects.filter(pmProduct=product_obj)
                    #每一个product对应了多个物料,和数量,遍历这些参数,便于增减
                    for index in product_index:
                        material_obj = index.pmMaterial
                        #将产品数量*对应物料的消耗个数
                        if material_obj.amount < index.pmAmount*item_amount:
                            error_msg =material_obj.uniqueId+":库存不足,无法出库"
                            addErrorlog(request,error_msg,pageNow)
                            tag_out = "Error:"+error_msg
                            ret = {"tag_out":tag_out}
                            return HttpResponse(json.dumps(ret))
                        else:
                            material_obj.amount -= index.pmAmount*item_amount
                            material_obj.save()
                    item_weight = getWeight(product_obj.weight)
                    item_volume = getVolume(product_obj.length,product_obj.width,product_obj.height)
                    if product_obj.freightFee and product_obj.freightFee != 0:
                        item_freightfee = product_obj.freightFee
                    elif item_volume != 0 and product_obj.dhlShippingFee:
                        item_freightfee = product_obj.dhlShippingFee
                    else:
                        item_freightfee = 0 
                    item_weight_sum = item_weight*item_amount
                    item_volume_sum = item_volume*item_amount
                    item_freightfee_sum = item_freightfee*item_amount
                    #创建outitem对象
                    item_object = models.OutItem.objects.create(master=outstock_obj,productName=product_obj,amountOut=item_amount,\
                        site=_site,freightfee=item_freightfee_sum,weight=item_weight_sum,volume=item_volume_sum)
                    weight_list.append(item_weight_sum)
                    volume_list.append(item_volume_sum)
                    fee_list.append(item_freightfee_sum)
            total_weight = float(sum(weight_list))
            total_volume = float(sum(volume_list))
            total_fee = float(sum(fee_list))
            outstock_obj.total_weight = total_weight
            outstock_obj.total_volume = total_volume
            outstock_obj.total_freightfee = total_fee
            #为出库对象增加属性
            outstock_obj.save()
            tag_out = "成功出库,编号:"+new_code
            ret = {"tag_out":tag_out}
            return HttpResponse(json.dumps(ret))
        
        

def preOutstockList(request):
    if not request.session.get('is_login',None):
        return redirect('/index')
    preoutstocks = models.PreOutstock.objects.all().order_by('-id')
    return render(request,'preoutstocklist.html',locals())


        
class PreOutstockDetail(View):
    def get(self,request,id):
        if not request.session.get('is_login',None):
            return redirect('/index')
        try:
            preoutstock = models.PreOutstock.objects.get(id=id)
            preoutitems = models.PreOutitem.objects.filter(master=id)
        except:
            pass
        message="已读取预出库表"
        count = len(preoutitems)
        return render(request,'preoutstockdetail.html',locals())
    def post(self,request):
        pass
        













 

