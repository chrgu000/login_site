# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import models
from django.contrib import admin
from django.utils.safestring import mark_safe
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display=('name','email','password')
    
# class WarehouseAdmin(admin.ModelAdmin):
    # list_display=('code','location','status','users')
    

class ProductAdmin(admin.ModelAdmin):
    list_display=('uniqueid','feature','description','count','purchase_price','sale_price','warehouse','user','image')

class MaterialAdmin(admin.ModelAdmin):
    list_display=("uniqueId","amount")

class ProductTempAdmin(admin.ModelAdmin):
    list_display = ("site","sku","childAsin")

class AutoLogAdmin(admin.ModelAdmin):
    list_display = ("date","user","act")

# class AutoLogAdmin(admin.ModelAdmin):
    # def get_readonly_fields(self, request, obj=None):
        # """  重新定义此函数，限制普通用户所能修改的字段  """
        # if request.user.is_superuser:
            # self.readonly_fields = []
        # return self.readonly_fields
    # readonly_fields = ('date',)



admin.site.register(models.User,UserAdmin)
# admin.site.register(models.Warehouse,WarehouseAdmin)
# admin.site.register(models.Product,ProductAdmin)
admin.site.register(models.Uploadfiles)
admin.site.register(models.ProductTemp,ProductTempAdmin)
admin.site.register(models.InventoryMaterial,MaterialAdmin)
admin.site.register(models.OutStock)
admin.site.register(models.Site)
admin.site.register(models.InStock)
admin.site.register(models.AutoLog)

admin.site.site_url = '/index/'#修改admin中的viewsite的默认值