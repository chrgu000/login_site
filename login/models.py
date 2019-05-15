# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.utils.text import force_text
from django.db import models
import time,os
## from filer.fields.image  import FilerImageField

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
    can_component = models.BooleanField(_("可作为零件组合使用"),default=True)
    image = models.ImageField(_("图片"),upload_to='photos',blank=True,null=True,default='photos/americanfootball_NSqvub1.jpg ')
    
    def __unicode__(self):
        return self.nickname
    class Meta:
        # ordering = ["-adate"]
        verbose_name = "商品"
        verbose_name_plural = "商品"

#将获取的文件名加上当前日期,输出新地址/newmedia/filename+date.xlxs
# def upload_productpath(filename):
    # ext = filename.split('.')[-1]
    # name = filename.split('.')[0]
    # fullname = name+time.strftime("%Y%m%d",time.localtime())
    # filename_new = "{}.{}".format(fullname,ext)
    # return os.path.join('uploadfiles',filename_new)
    
class Uploadfiles(models.Model):
    
    uploaduser = models.CharField(max_length=20,blank=True,null=True,verbose_name=_("批量上传人员"))
    date = models.CharField(verbose_name=_("上传时间"),max_length=20,blank=True,null=True)
    file_name = models.CharField(max_length=50,blank=True,null=True,verbose_name=_("文件名"))

    def __unicode__(self):
        return self.file_name
    
    class Meta:
        verbose_name = "上传文件历史记录"
        verbose_name_plural = "上传文件历史记录"


class Material(models.Model):
    #测试物料表
    mName = models.CharField(_("物料名称"),max_length=50)
    mAmount = models.IntegerField(_("库存数量"),blank=True,null=True,default=0)
    
    def __unicode__(self):
        return self.mName


    
class InventoryMaterial(models.Model):

    amount = models.IntegerField(_("库存数量"),blank=True,null=True,default=0)
    description = models.TextField(_("详细信息"),max_length=200,blank=True,null=True)
    uniqueId =  models.CharField(verbose_name=_("唯一识别码"),max_length=100,blank=True,null=True)
    userPurchase = models.ForeignKey(User,verbose_name=_("采购人员"),blank=True,null=True)
    image = models.ImageField(_("图片"),upload_to='photos',blank=True,null=True,default="/photos/americanfootball.jpg")
    price = models.DecimalField(verbose_name=_("采购价(rmb)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)

    def __unicode__(self):
        return self.uniqueId
    class Meta:
        verbose_name = "物料"
        verbose_name_plural = "物料"
    
class InStock(models.Model):
    code = models.CharField(verbose_name=_("入库编号"),max_length=50)
    c_time = models.CharField(verbose_name=_("入库时间"),max_length=50)
    description = models.TextField(_("入库信息"),max_length=200,blank=True,null=True)
    userInstock = models.ForeignKey(User,blank=True,null=True,verbose_name=_("入库人员"))
    
    def __unicode__(self):
        return self.description
        
    class Meta:
        ordering = ["c_time"]
        verbose_name = "入库表"
        verbose_name_plural = "入库表"

class InItem(models.Model):
    master = models.ForeignKey(InStock,verbose_name=_("入库表"),on_delete=models.CASCADE)
    materialName = models.ForeignKey(InventoryMaterial,verbose_name=_("物料名称"))
    amountIn =  models.PositiveIntegerField(_("入库数量"),blank=True,null=True)
    
    def __unicode__(self):
        return self.materialName
        
    class Meta:
        verbose_name = "入库项"
        verbose_name_plural = "入库项"

class Site(models.Model):
    name = models.CharField(_("站点名称"),max_length=50)
    
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "站点"
        verbose_name_plural = "站点"




class ProductTemp(models.Model):
    # 测试产品表
    pMaterial = models.ManyToManyField(InventoryMaterial,through='ProductMaterial')
    site = models.ForeignKey(Site,verbose_name=_("站点"),blank=True,null=True)
    sku = models.CharField(verbose_name=_("SKU"),unique=True,max_length=200,blank=True,null=True)    
    childAsin = models.CharField(verbose_name=_("child ASIN"),max_length=50,blank=True,null=True)
    title = models.TextField(_("Title"),max_length=400,blank=True,null=True)
    purchasePrice = models.DecimalField(verbose_name=_("采购价格(rmb)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    weight = models.DecimalField(verbose_name=_("包装重量(kg)"),max_digits=15,decimal_places=3,blank=True,null=True,default=0)
    length = models.DecimalField(verbose_name=_("包装尺寸长(cm)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    width = models.DecimalField(verbose_name=_("包装尺寸宽(cm)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    height = models.DecimalField(verbose_name=_("包装尺寸高(cm)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    volumeWeight = models.DecimalField(verbose_name=_("包装体积重(kg)"),max_digits=15,decimal_places=3,blank=True,null=True,default=0)
    dhlShippingFee = models.DecimalField(verbose_name=_("DHL海运费(rmb)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    packageFee = models.DecimalField(verbose_name=_("物料费(rmb)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    opFee = models.DecimalField(verbose_name=_("运营费(rmb)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    currency = models.DecimalField(verbose_name=_("汇率(us-chn)"),max_digits=15,decimal_places=5,blank=True,null=True,default=0)
    fbaFullfillmentFee = models.DecimalField(verbose_name=_("FBA运费(dollar)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    shrinkage = models.DecimalField(verbose_name=_("产品损耗(dollar)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    amazonReferralFee = models.DecimalField(verbose_name=_("amazon平台费(%)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    payoneerServiceFee = models.DecimalField(verbose_name=_("Payoneer服务费(%)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    
    amazonSalePrice = models.DecimalField(verbose_name=_("售价(dollar)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    margin = models.DecimalField(verbose_name=_("利润(dollar)"),max_digits=15,decimal_places=3,blank=True,null=True,default=0)
    marginRate = models.DecimalField(verbose_name=_("利润率(%)"),max_digits=15,decimal_places=3,blank=True,null=True,default=0)
    productCostPercentage = models.DecimalField(verbose_name=_("产品成本(%)"),max_digits=6,decimal_places=2,blank=True,null=True,default=0)
    image = models.ImageField(_("图片"),upload_to='photos',blank=True,null=True,default='photos/americanfootball_NSqvub1.jpg ')
    description = models.TextField(_("中文备注"),max_length=200,blank=True,null=True)
    creater = models.ForeignKey(User,blank=True,null=True,verbose_name=_("创建人员"))
    c_time = models.CharField(verbose_name=_("创建时间"),max_length=50,blank=True,null=True)
    adcost = models.DecimalField(verbose_name=_("广告费(dollar)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0) 
    freightFee = models.DecimalField(verbose_name=_("实际运费(%)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)
    tagpath = models.CharField(verbose_name=_("标签地址"),max_length=150,blank=True,null=True)
    
    def __unicode__(self):
        return self.sku
    class Meta:
        verbose_name = "产品"
        verbose_name_plural = "产品"

class ProductMaterial(models.Model):
    # 测试产品物料关系表
    pmMaterial = models.ForeignKey(InventoryMaterial,on_delete=models.CASCADE)
    pmProduct = models.ForeignKey(ProductTemp,on_delete=models.CASCADE)
    pmAmount = models.PositiveIntegerField(_("使用数量"),blank=True,null=True)

class OutStock(models.Model):
    #出库批次
    code = models.CharField(verbose_name=_("出库编号"),max_length=50)
    #入库用的DateTimeField,接收html的数据需要转换,干脆char
    c_time = models.CharField(verbose_name=_("入库时间"),max_length=50)
    description = models.TextField(_("出库信息"),max_length=200,blank=True,null=True)
    userOutstock = models.ForeignKey(User,blank=True,null=True,verbose_name=_("出库人员"))
    total_weight = models.DecimalField(verbose_name=_("总重量(kg)"),max_digits=15,decimal_places=3,blank=True,null=True,default=0)
    total_volume = models.DecimalField(verbose_name=_("总体积(m3)"),max_digits=15,decimal_places=3,blank=True,null=True,default=0)
    total_freightfee = models.DecimalField(verbose_name=_("总运费(rmb)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)

    def __unicode__(self):
        return self.description
    class Meta:
        verbose_name = "出库表"
        verbose_name_plural = "出库表"

class OutItem(models.Model):
    master = models.ForeignKey(OutStock,verbose_name=_("出库表"),on_delete=models.CASCADE)
    site = models.CharField(verbose_name=_("站点"),max_length=30,blank=True,null=True)
    productName = models.ForeignKey(ProductTemp,verbose_name=_("产品名称"))
    amountOut =  models.PositiveIntegerField(_("出库数量"),blank=True,null=True)
    freightfee = models.DecimalField(_("运费"),blank=True,null=True,max_digits=15,decimal_places=2)
    weight = models.DecimalField(_("包装重量(kg)"),blank=True,null=True,max_digits=15,decimal_places=3)
    volume = models.DecimalField(_("包装体积(m3)"),blank=True,null=True,max_digits=15,decimal_places=3)
    def __unicode__(self):
        return self.prodcutName

    class Meta:
        verbose_name = "出库项"
        verbose_name_plural = "出库项"

class AutoLog(models.Model):
    date = models.CharField(verbose_name=_("操作时间"),max_length=200,blank=True,null=True)
    user = models.ForeignKey(User,verbose_name=_("用户名"),blank=True,null=True)
    act = models.CharField(verbose_name=_("操作行为"),max_length=200,blank=True,null=True)
    
    def __unicode__(self):
        return self.date
    class Meta:
        verbose_name = "日志"
        verbose_name_plural = "日志"
        
class ErrorLog(models.Model):
    date = models.CharField(verbose_name=_("时间"),max_length=200,blank=True,null=True)
    user = models.ForeignKey(User,verbose_name=_("用户名"),blank=True,null=True)
    message = models.CharField(verbose_name=_("报错信息"),max_length=200,blank=True,null=True)
    page = models.CharField(verbose_name=_("页面"),max_length=200,blank=True,null=True)
    
    def __unicode__(self):
        return self.date
    class Meta:
        verbose_name = "报错日志"
        verbose_name_plural = "报错日志"

class PreOutstock(models.Model):
    pcode = models.CharField(verbose_name=_("预出库编号"),max_length=50)
    ptime = models.CharField(verbose_name=_("编辑时间"),max_length=50)
    pdescription = models.TextField(_("备注信息"),max_length=200,blank=True,null=True)
    user = models.ForeignKey(User,blank=True,null=True,verbose_name=_("操作人员"))
    total_weight = models.DecimalField(verbose_name=_("总重量(kg)"),max_digits=15,decimal_places=3,blank=True,null=True,default=0)
    total_volume = models.DecimalField(verbose_name=_("总体积(m3)"),max_digits=15,decimal_places=3,blank=True,null=True,default=0)
    total_freightfee = models.DecimalField(verbose_name=_("总运费(rmb)"),max_digits=15,decimal_places=2,blank=True,null=True,default=0)

    def __unicode__(self):
        return self.pcode
    class Meta:
        verbose_name = "预出库表"
        verbose_name_plural = "预出库表"

class PreOutitem(models.Model):
    master = models.ForeignKey(PreOutstock,verbose_name=_("预出库表"),on_delete=models.CASCADE)
    productName = models.ForeignKey(ProductTemp,verbose_name=_("产品名称"))
    amount =  models.PositiveIntegerField(_("预出库数量"),blank=True,null=True)

    def __unicode__(self):
        return self.prodcutName

    class Meta:
        verbose_name = "预出库项"
        verbose_name_plural = "预出库项"






















 
