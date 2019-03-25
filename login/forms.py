# -*- coding:utf-8 -*- 
from django import forms
from login import models
from captcha.fields import CaptchaField

class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label='验证码')
    
class RegisterForm(forms.Form):
    gender = (
        ('male', "男"),
        ('female', "女"),
    )
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(label='性别', choices=gender)
    captcha = CaptchaField(label='验证码')

# class AddproductForm(forms.ModelForm):
    # class Meta:
        # model = models.Product
        # fields = ['nickname','adate','feature','description','count','purchase_price',
        # 'sale_price','warehouse','user','can_sale','can_component','image']


    # def __init__(self,*args,**kwargs):
        # super(AddproductForm,self).__init__(*args,**kwargs)
        # self.fields['nickname'].label = "英文名称"
        # self.fields['adate'].label = "时间编号"
        # self.fields['feature'].label = "英文简要特征"
        # self.fields['description'].label = "中文详细描述"
        # self.fields['count'].label = "库存数量"
        # self.fields['purchase_price'].label = "进货价格"
        # self.fields['sale_price'].label = "销售价格"
        # self.fields['warehouse'].label = "存放仓库"
        # self.fields['user'].label = "录入人员"
        # self.fields['can_sale'].label = "可销售"
        # self.fields['can_component'].label = "可作为零件组合使用"
        # self.fields['image'].label = '产品图片'
        # self.fields['image'].label = '上传图片'

# class UploadfilesForm(forms.ModelForm):
    # class Meta:
        # model = models.Uploadfiles
        # fields = ['uploaduser','date','file_name']
        
    # def __init__(self,*args,**kwargs):
        # super(UploadfilesForm,self).__init__(*args,**kwargs)
        # self.fields['uploaduser'].label = "批量上传人员"
        # self.fields['date'].label = "上传时间"
        # self.fields['file_name'].label = "上传文件"

class InventoryInitForm(forms.ModelForm):
    class Meta:
        model = models.InventoryMaterial
        fields = "__all__"
    def __init__(self,*args,**kwargs):
        super(InventoryInitForm,self).__init__(*args,**kwargs)

        self.fields['amount'].label = "库存数量"
        self.fields['description'].label = "详细信息"
        self.fields['uniqueId'].label = '唯一识别码'
        self.fields['userPurchase'].label = '采购人员'
        self.fields['image'].label = '上传图片'

class ProductTempForm(forms.ModelForm):
    class Meta:
        model = models.ProductTemp
        exclude = ('pMaterial',)
    def __init__(self,*args,**kwargs):
        super(ProductTempForm,self).__init__(*args,**kwargs)

        self.fields['site'].label = '站点'
        self.fields['sku'].label = 'SKU'
        self.fields['childAsin'].label = 'child ASIN'
        self.fields['title'].label = 'Title'
        self.fields['purchasePrice'].lable = '采购价格(rmb)'
        self.fields['weight'].lable = '包装重量(kg)'
        self.fields['length'].lable = '包装尺寸长(cm)'
        self.fields['width'].lable = '包装尺寸宽(cm)'
        self.fields['height'].lable = '包装尺寸高(cm)'
        self.fields['volumeWeight'].lable = '包装体积重(kg)'
        self.fields['dhlShippingFee'].lable = 'DHL海运费(rmb)'
        self.fields['packageFee'].lable = '物料费(rmb)'
        self.fields['opFee'].lable = '运营费(rmb)'
        self.fields['currency'].lable = '汇率(us-chn)'
        self.fields['fbaFullfillmentFee'].lable = 'FBA运费(dollar)'
        self.fields['shrinkage'].lable = '产品损耗(dollar)'
        self.fields['adcost'].lable = "广告费(dollar)"
        self.fields['amazonReferralFee'].lable = 'amazon平台费(%)'
        self.fields['payoneerServiceFee'].lable = 'Payoneer服务费(%)'
        self.fields['amazonSalePrice'].lable = '售价(dollar)'
        self.fields['margin'].lable = '利润(dollar)'
        self.fields['marginRate'].lable = '利润率(%)'
        self.fields['image'].lable = '图片'
        self.fields['description'].lable = '中文备注'
        self.fields['creater'].label ='创建人'
        self.fields['c_time'].label = '创建时间'






 
 



























