# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.utils.text import force_text
from django.db import models
# from filer.fields.image  import FilerImageField

# Create your models here.

class User(models.Model):

    gender = (
        ('male', "男"),
        ('female', "女"),
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default="男")
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["c_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"

class Warehouse(models.Model):
    code = models.CharField(_("仓库编号"),max_length=20,blank=True,null=True)
    name = models.CharField(_("仓库名称"),max_length=40)
    status = models.BooleanField(_("是否可用"),default=True)
    location = models.CharField(_("仓库地址"),max_length=120,blank=True,null=True)
    users = models.ForeignKey(User,verbose_name=_("相关人员"),blank=True,null=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('仓库')
        verbose_name_plural = _('仓库')



class Product(models.Model):

    nickname = models.CharField(_("英文名称"),max_length=50)
    feature = models.CharField(_("英文简要特征"),max_length=50,blank=True,null=True)
    uniqueid = models.CharField(_("唯一识别码"),max_length=50,blank=True,null=True)
    adate = models.CharField(_("时间编号"),max_length=20,blank=True,null=True)
    description = models.TextField(_("中文详细描述"),max_length=200,blank=True,null=True)
    count = models.PositiveIntegerField(_("库存数量"),blank=True,null=True)
    purchase_price = models.DecimalField(_("进货价格"),max_digits=14,decimal_places=4,blank=True,null=True)
    sale_price = models.DecimalField(_("销售价格"),max_digits=14,decimal_places=4,blank=True,null=True)
    warehouse = models.ForeignKey(Warehouse,blank=True,null=True,verbose_name=_("warehouse"))
    user = models.ForeignKey(User,blank=True,null=True,verbose_name=_("入库人员"))
    can_sale = models.BooleanField(_("可销售"),default=True)
    can_component = models.BooleanField(_("可作为零件组合使用"))
    image = models.ImageField(_("图片"),upload_to='photos',blank=True,null=True,default='photos/americanfootball_NSqvub1.jpg ')
    
    def __unicode__(self):
        return self.nickname
    class Meta:
        ordering = ["-adate"]
        verbose_name = "商品"
        verbose_name_plural = "商品"

 
