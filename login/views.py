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
import time,os
import xlrd,xlwt
from random import randint
import collections


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
            user = request.session.get('_auth_user_id')
            user_obj = models.User.objects.get(id=user)
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


# def result(request):

# def inventoryMaterial(request):
    # if not request.session.get('is_login',None):
        # return redirect('/index')
    # inventorymaterials = models.InventoryMaterial.objects.all()
    # return render(request,"inventorymaterial.html",locals())

class InventoryMaterial(View):
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
        users = models.User.objects.all()
        return render(request,'inventoryinit.html',locals())
        
    def post(self,request):
        new_amount = request.POST.get('amount')
        new_description = request.POST.get('description')
        new_uid = request.POST.get('uniqueid')
        new_user = request.POST.get('user')
        new_image = request.FILES.get('image',None)
        
        if new_amount=="" or new_description=="" or new_uid=="":
            return HttpResponse("请填写表单所有项目")
        else:
            uid_exist = models.InventoryMaterial.objects.filter(uniqueId__contains = str(new_uid))
            if uid_exist :
                return HttpResponse("唯一识别码重复,请重新录入")
            
            else:
                user_obj = models.User.objects.get(name=new_user)
                material_obj = models.InventoryMaterial.objects.create(amount=new_amount,description=new_description,\
                            uniqueId=new_uid,userPurchase=user_obj,image=new_image)
                
                message = "录入成功"
                return render(request,'inventoryinit.html',locals())





def inStock(request):
    if not request.session.get('is_login',None):
        return redirect('/index')
    instocks = models.InStock.objects.all()
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
        user = request.session.get('_auth_user_id')
        user_obj = models.User.objects.get(id=user)
        print user_obj.name
        return render(request,'instockadd.html',locals())
    
    def post(self,request):
        new_code = request.POST.get('code')
        new_c_time = request.POST.get('c_time')
        new_description = request.POST.get('description')
        
        user = request.session.get('_auth_user_id')
        user_obj = models.User.objects.get(id=user)
        # if new_code is None or new_c_time is None or new_description is None:
        if new_code == "" or new_c_time == "" or new_description == "":
            return HttpResponse("请填写表单所有项目")
        
        else:
            # 对code查重
            code_exist = models.InStock.objects.filter(code__contains = str(new_code))
            if code_exist:
                return HttpResponse("入库编号重复,请重新录入")
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


        return render(request, 'instockadd.html', locals()) 
        
    

def inItem(request):
    inventorymaterials = models.InventoryMaterial.objects.all().order_by("uniqueId")
    #加了检索以后,开新页会导致无法关联到新增页,解决前先不加.
    # q = request.GET.get('q','') #检索内容
    # 检索部分的选择
    # if q:
        # inventorymaterials = inventorymaterials.filter(Q(uniqueId__icontains=q) | 
            # Q(description__icontains=q) | Q(amount__icontains=q))
    # else:
        # pass
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
        user = request.session.get('_auth_user_id')
        user_obj = models.User.objects.get(id=user)
        return render(request,'uploadmaterial.html',locals())
    
    def post(self,request):
        
        new_c_time = request.POST.get('c_time')#对应date
        new_code = request.POST.get('code')#对应modifyindex
        new_description = request.POST.get('description')
        File = request.FILES.get('files',None)

        if File is None or new_c_time == "" or new_code == "":
            return HttpResponse("请完整填写表单")
        else:
            # 对code查重
            code_exist = models.InStock.objects.filter(code__contains = str(new_code))
            if code_exist:
                return HttpResponse("入库编号重复,请重新录入")
            
            else:
                #创建instock对象
                user = request.session.get('_auth_user_id')
                user_obj = models.User.objects.get(id=user)
                instock_obj = models.InStock.objects.create(code=new_code,c_time=new_c_time,description=new_description,userInstock=user_obj)
                
                
                type_excel = File.name.split('.')[-1]
                if 'xlsx'== type_excel:
                    upload_obj = models.Uploadfiles.objects.create(uploaduser=user_obj.name,date=new_c_time,file_name=File.name)
                    wb = xlrd.open_workbook(filename=None,file_contents=File.read())
                    table = wb.sheets()[0]
                    nrows = table.nrows
                    # print upload_obj
                    
                    try:
                        with transaction.atomic():
                            for i in range(1,nrows):
                                rowValues = table.row_values(i)
                                uniq = rowValues[0]
                                purchaseuser = rowValues[3]
                                #user是外键,找出对应的对象
                                uniq_obj = models.InventoryMaterial.objects.filter(uniqueId=uniq)
                                # print uniq_obj

                                #如果uniqID重复了,说明是追加入库,只修改数量和修改index
                                if uniq_obj:
                                    #用filter找出的对象无法存储,只好用get再取一次
                                    #uniq_get是物料对象
                                    uniq_get = models.InventoryMaterial.objects.get(uniqueId=uniq)
                                    uniq_get.amount += abs(int(rowValues[2]))
                                    uniq_get.save()
                                #如果不重复,说明是首次,创建新的物料对象
                                else:
                                    userPur = models.User.objects.get(name = purchaseuser)
                                    print user
                                    models.InventoryMaterial.objects.create(uniqueId=rowValues[0],description=rowValues[1],
                                        amount=rowValues[2],userPurchase=userPur)
                                material_obj = models.InventoryMaterial.objects.get(uniqueId=uniq)
                                item_amount = abs(int(rowValues[2]))
                                item_object = models.InItem.objects.create(master=instock_obj,materialName=material_obj,amountIn=item_amount)
                                print "create initem object"
                            
                            message = "已完成上传,请在入库详情中查看."
                            return render(request,'uploadmaterial.html',locals())

                    except Exception as e:
                        return HttpResponse("出现错误")
                else:
                    return HttpResponse("上传文件格式不是xlsx")


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
    fee2 = (fee1+fbafee+adcost)*0.945
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
    fee1 = amazonprice*(1-amazonfee/100)
    fee2 = fbafee+shrinkage+adcost
    fee3 = (fee1-fee2)*(1-payonfee/100)*currency
    fee4 = fee3-(purprice+shrinkage+packfee+opfee) #margin
    fee5 = fee4/(amazonprice*currency)#marginrate
    return fee4,fee5

def calProductCostPercentage(purprice,amazonprice,currency):
    purprice = float(purprice)
    amazonprice=float(amazonprice)
    currency = float(currency)
    fee = purprice/(amazonprice*currency)
    return fee


class Addproducttemp(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写表单"
        user = request.session.get('_auth_user_id')
        user_obj = models.User.objects.get(id=user)
        sites = models.Site.objects.all()
        return render(request,'addproducttemp.html',locals())
        
    def post(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
            
        user = request.session.get('_auth_user_id')
        user_obj = models.User.objects.get(id=user)
        
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
        
        if new_sku =="" or new_childasin=="" or new_title=="" or new_description=="" or new_date=="":
            return HttpResponse("请完成表单必填内容")
        else:
            sku_exist = models.ProductTemp.objects.filter(sku__contains =str(new_sku))
            if sku_exist:
                return HttpResponse("sku重复,请重新录入")
            else:
                if purchaseprice =="0.00" or weight=="0.000" or length=="0.00" or width=="0.00" or height=="0.00" or volumeweight=="0.000" or packagefee=="0.00"\
                    or opfee=="0.00" or fbafee=="0.00" or amazonfee=="0.00" or payserfee=="0.00" or adcost=="0.00" or amazonprice=="0.00":

                    product_obj = models.ProductTemp.objects.create(sku = new_sku,childAsin=new_childasin,title=new_title,\
                            description=new_description,creater=user_obj,c_time=new_date,site=site_obj,purchasePrice=purchaseprice,weight=weight,\
                            length=length,width=width,height=height,volumeWeight=volumeweight,packageFee=packagefee,opFee=opfee,\
                            currency=currency,fbaFullfillmentFee=fbafee,amazonReferralFee=amazonfee,payoneerServiceFee=payserfee,\
                            amazonSalePrice=amazonprice,adcost=adcost,image=new_image)
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
                    # message = "产品已创建,因备选内容不完整,故无法产生公式项"
                    return HttpResponse("产品已创建,因备选内容不完整,故无法产生公式项")
                else:
                    _dhlfee = calDHLShippingFee(weight,length,width,height)
                    _shrinkage = calShrinkage(purchaseprice,_dhlfee,packagefee,opfee,currency,fbafee,adcost)
                    _margin,_marginRate = calMargin(purchaseprice,_dhlfee,packagefee,opfee,currency,fbafee,_shrinkage,adcost,amazonfee,payserfee,amazonprice)
                    _productCostP = calProductCostPercentage(purchaseprice,amazonprice,currency)
                    product_obj = models.ProductTemp.objects.create(sku = new_sku,childAsin=new_childasin,title=new_title,\
                            description=new_description,creater=user_obj,c_time=new_date,site=site_obj,purchasePrice=purchaseprice,weight=weight,\
                            length=length,width=width,height=height,volumeWeight=volumeweight,packageFee=packagefee,opFee=opfee,\
                            currency=currency,fbaFullfillmentFee=fbafee,amazonReferralFee=amazonfee,payoneerServiceFee=payserfee,\
                            amazonSalePrice=amazonprice,adcost=adcost,image=new_image,dhlShippingFee=_dhlfee,shrinkage=_shrinkage,\
                            margin=_margin,marginRate=_marginRate,productCostPercentage=_productCostP)
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
    
    outstocks = models.OutStock.objects.all()
    return render(request,'outstock.html',locals())

def outStockDetail(request,id):
    if not request.session.get('is_login',None):
        return redirect('/index')
    try:
        #通过outstock的id找出对象
        print id 
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
        user = request.session.get('_auth_user_id')
        user_obj = models.User.objects.get(id=user)
        return render(request,'outstockadd.html',locals())
    
    #获取表单对象,对表单数据进行净化判断,对出库对象进行处理
    def post(self,request):
        new_code = request.POST.get('code')
        new_c_time = request.POST.get('c_time')
        new_description = request.POST.get('description')
        
        user = request.session.get('_auth_user_id')
        user_obj = models.User.objects.get(id=user)
        #检查空值
        if new_code == "" or new_c_time == "" or new_description == "":
            return HttpResponse("请完整填写表单")
        else:
            code_exist = models.OutStock.objects.filter(code__contains = str(new_code))
            if code_exist:
                return HttpResponse("出库编号重复,请重新输入")
                
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
                                return HttpResponse(str(material_obj.pmMaterial)+":库存不足,无法出库")
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

                return render(request,'outstockadd.html',locals())


def outItem(request):
    producttemps = models.ProductTemp.objects.all()
    return render(request,'outitem.html',locals())


class Uploadoutstock(View):
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写表单并选择上传文件"
        user = request.session.get('_auth_user_id')
        user_obj = models.User.objects.get(id=user)
        return render(request,'uploadoutstock.html',locals())
    
    def post(self,request):
        user = request.session.get('_auth_user_id')
        user_obj = models.User.objects.get(id=user)
        new_c_time = request.POST.get('c_time')
        new_code = request.POST.get('code')
        new_description = request.POST.get('description')
        File = request.FILES.get('files',None)
        if File is None or new_c_time == "" or new_code == "":
            return HttpResponse("请完整填写表单")
        else:
            # 对code查重
            code_exist = models.OutStock.objects.filter(code__contains = str(new_code))
            if code_exist:
                return HttpResponse("出库编号重复,请重新录入")
                
            else:
                #这里先建立outstock对象,再逐个产品创建outitem对象

                outstock_obj = models.OutStock.objects.create(code=new_code,c_time=new_c_time,description=new_description,userOutstock=user_obj)
                
                type_excel = File.name.split('.')[-1]
                if 'xlsx'== type_excel:
                    
                    upload_obj = models.Uploadfiles.objects.create(uploaduser=user_obj,date=new_c_time,file_name=File.name)
                    wb = xlrd.open_workbook(filename=None,file_contents=File.read())
                    table = wb.sheets()[0]
                    nrows = table.nrows

                    try:
                        with transaction.atomic():
                            for i in range(2,nrows):
                                rowValues = table.row_values(i)
                                _sku = rowValues[1]
                                amountout = int(rowValues[2])
                                pt_test = models.ProductTemp.objects.filter(sku=_sku)
                                
                                if pt_test:
                                    
                                    product_obj = models.ProductTemp.objects.get(sku=_sku)
                                    product_index = models.ProductMaterial.objects.filter(pmProduct=product_obj)
                                    for index in product_index:
                                        material_obj = index.pmMaterial
                                        if material_obj.amount < index.pmAmount*amountout:
                                            return HttpResponse("库存不足,无法出库")
                                        else:
                                            material_obj.amount -= index.pmAmount*amountout
                                            material_obj.save()
                                    #对一种产品的循环完成后,对该产品的出库创建对象
                                    _dhlfee = int(rowValues[3])
                                    _totalfee = _dhlfee*amountout
                                    models.OutItem.objects.create(master=outstock_obj,productName=product_obj,amountOut=amountout,\
                                        siteinput=rowValues[0],dhlshippingfeeInput=_dhlfee,totalfee=_totalfee)

                                else:
                                    return HttpResponse("childAsin:"+childasin+"   该产品未创建,无法出库")
                            message = "上传完成"
                            # outstock = models.OutStock.objects.get(code=new_code)
                            # outitems = models.OutItem.objects.filter(master=outstock)
                            return render(request,'uploadoutstock.html',locals())
                    except Exception as e:
                        return HttpResponse("出现错误,未完成上传")
                else:
                    return HttpResponse("上传文件格式不是xlsx")

def searchtest(request):
    return render(request,"searchtest.html")

class Uploadnewpro(View):
    
    def get(self,request):
        if not request.session.get('is_login',None):
            return redirect('/index')
        message = "请填写表单并选择上传文件"
        user = request.session.get('_auth_user_id')
        user_obj = models.User.objects.get(id=user)
        return render(request,'uploadnewpro.html',locals())

    def post(self,request):
        user = request.session.get('_auth_user_id')
        new_c_time = request.POST.get('c_time')
        user_obj = models.User.objects.get(id=user)
        File = request.FILES.get('files',None)
        if File is None or new_c_time == "" :
            return HttpResponse("请完整填写表单")
        else:
            type_excel = File.name.split('.')[-1]
            if 'xlsx'== type_excel:
                upload_obj = models.Uploadfiles.objects.create(uploaduser=user_obj,date=new_c_time,file_name=File.name)
                wb = xlrd.open_workbook(filename=None,file_contents=File.read())
                table = wb.sheets()[0]
                nrows = table.nrows
                ncols = table.ncols
                
                #原子化
                for i in range(2,nrows):
                    rowValues = table.row_values(i)
                    
                    new_sku = rowValues[1]
                    new_childasin = rowValues[2]
                    new_title = rowValues[3]
                    new_site = rowValues[0]
                    print new_sku
                    print new_site
                    
                    if new_sku=="" or new_childasin=="" or new_title=="" or new_site=="":
                        tips = "第"+str(i)+"行的必填项目不完整,请检查上传文件."
                        return HttpResponse(tips)
                    else:
                        site_exist = models.Site.objects.filter(name=new_site)
                        sku_exist = models.ProductTemp.objects.filter(sku=new_sku)
                        new_description = rowValues[24]
                        if not sku_exist and site_exist :
                            site_obj = models.Site.objects.get(name=new_site)
                            tagE = 1#判断是否有空项
                            
                            # purchaseprice = "0.00"
                            # weight = "0.000"
                            # length = "0.00"
                            # width = "0.00"
                            # height = "0.00"
                            # volumeweight = "0.000"
                            # packagefee = "0.00"
                            # opfee = "0.00"
                            # currency = "6.50000"
                            # fbafee = "0.00"
                            # amazonfee = "0.00"
                            # payserfee = "0.00"
                            # adcost = "0.00"
                            # amazonprice = "0.00"
                            
                            list_col = [4,5,6,7,8,9,11,12,13,14,16,17,18,19]

                            # list_item = [purchaseprice,weight,length,width,height,volumeweight,packagefee,opfee,currency,\
                                        # fbafee,adcost,amazonfee,payserfee,amazonprice]

                            #如果表格中有空值,那么该列为默认值;如果有值,就使用
                            # for col,item in zip(list_col,list_item):
                                # if rowValues[col] == "":
                                    # print str(col)
                                    # tagE = 0
                                # else:
                                    # item = rowValues[col]
                                    # print item
                            # dic_items = {"purchaseprice":"0.00","weight":"0.000","length":"0.00","width":"0.00",\
                                # "height":"0.00","volumeweight":"0.000","packagefee":"0.00","opfee":"0.00","currency":"6.50000",\
                                # "fbafee":"0.00","amazonfee":"0.00","payserfee":"0.00","adcost":"0.00","amazonprice":"0.00"} 
                            dic_items = collections.OrderedDict([("purchaseprice","0.00"),("weight","0.000"),("length","0.00"),("width","0.00"),\
                                    ("height","0.00"),("volumeweight","0.000"),("packagefee","0.00"),("opfee","0.00"),("currency","6.50000"),\
                                    ("fbafee","0.00"),("adcost","0.00"),("amazonfee","0.00"),("payserfee","0.00"),("amazonprice","0.00")])
                            for col,item in zip(list_col,dic_items):
                                if rowValues[col] == "":
                                    tagE = 0
                                else:
                                    dic_items[item]=rowValues[col]

                            if tagE == 0 :
                                product_obj = models.ProductTemp.objects.create(sku = new_sku,childAsin=new_childasin,title=new_title,\
                                    description=new_description,creater=user_obj,c_time=new_c_time,site=site_obj,purchasePrice=dic_items["purchaseprice"],weight=dic_items["weight"],\
                                    length=dic_items["length"],width=dic_items["width"],height=dic_items["height"],volumeWeight=dic_items["volumeweight"],packageFee=dic_items["packagefee"],opFee=dic_items["opfee"],\
                                    currency=dic_items["currency"],fbaFullfillmentFee=dic_items["fbafee"],amazonReferralFee=dic_items["amazonfee"],payoneerServiceFee=dic_items["payserfee"],\
                                    amazonSalePrice=dic_items["amazonprice"],adcost=dic_items["adcost"])
                                print "pt_obj created"
                                for j in range(25,ncols,2):
                                    material_exist = models.InventoryMaterial.objects.filter(uniqueId=rowValues[j])
                                    if material_exist:
                                        material_obj = models.InventoryMaterial.objects.get(uniqueId=rowValues[j])
                                        material_amount = abs(int(rowValues[j+1]))
                                        pmrelation_obj = models.ProductMaterial.objects.create(pmMaterial=material_obj,pmProduct=product_obj,pmAmount=material_amount)
                                    elif rowValues[j]=="":
                                        break
                                    else :
                                        tips = "物料uniqueID:   "+str(rowValues[j])+"   未查询到,请检查数据."
                                        return HttpResponse(tips)
                            else:
                                #这里要计算那堆乱七八糟了.
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
                                    margin=_margin,marginRate=_marginRate,productCostPercentage=_productCostP)
                                print "pt_obj created"
                                for j in range(25,ncols,2):
                                    material_exist = models.InventoryMaterial.objects.filter(uniqueId=rowValues[j])
                                    if material_exist:
                                        material_obj = models.InventoryMaterial.objects.get(uniqueId=rowValues[j])
                                        material_amount = abs(int(rowValues[j+1]))
                                        pmrelation_obj = models.ProductMaterial.objects.create(pmMaterial=material_obj,pmProduct=product_obj,pmAmount=material_amount)
                                    elif rowValues[j]=="":
                                        break
                                    else :
                                        tips = "物料uniqueID:   "+str(rowValues[j])+"   未查询到,请检查数据."
                                        return HttpResponse(tips)
                        else:
                            tips = "第"+str(i)+"行站点名称未注册 或 sku重复."
                            return HttpResponse(tips)
                message = "上传完毕,请在产品表查看并核对"
                return render(request,'uploadnewpro.html',locals())

            else:
                return HttpResponse("上传文件格式不是xlsx")





















 

