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

class AddproductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ['nickname','adate','feature','description','count','purchase_price',
        'sale_price','warehouse','user','can_sale','can_component','image']
        # fields = ['nickname','adate','feature','description','count','purchase_price',
        # 'sale_price','warehouse','user','can_sale','can_component','image','image2']

    def __init__(self,*args,**kwargs):
        super(AddproductForm,self).__init__(*args,**kwargs)
        self.fields['nickname'].label = "英文名称"
        self.fields['adate'].label = "时间编号"
        self.fields['feature'].label = "英文简要特征"
        self.fields['description'].label = "中文详细描述"
        self.fields['count'].label = "库存数量"
        self.fields['purchase_price'].label = "进货价格"
        self.fields['sale_price'].label = "销售价格"
        self.fields['warehouse'].label = "存放仓库"
        self.fields['user'].label = "录入人员"
        self.fields['can_sale'].label = "可销售"
        self.fields['can_component'].label = "可作为零件组合使用"
        # self.fields['image'].label = '产品图片'
        self.fields['image'].label = '上传图片'




























