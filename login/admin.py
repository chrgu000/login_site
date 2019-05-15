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
    

# class ProductAdmin(admin.ModelAdmin):
    # list_display=('uniqueid','feature','description','count','purchase_price','sale_price','warehouse','user','image')

class MaterialAdmin(admin.ModelAdmin):
    list_display=("uniqueId","amount","description")

class ProductTempAdmin(admin.ModelAdmin):
    list_display = ("site","sku","childAsin","title")

class AutoLogAdmin(admin.ModelAdmin):
    list_display = ("date","user","act")

class UploadfilesAdmin(admin.ModelAdmin):
    list_display = ("date","uploaduser","file_name")

class PreOutstockAdmin(admin.ModelAdmin):
    list_display = ("pcode","ptime","pdescription")

class InstockAdmin(admin.ModelAdmin):
    list_display = ("code","c_time","description","userInstock")

class OutstockAdmin(admin.ModelAdmin):
    list_display = ("code","c_time","description","userOutstock","total_freightfee")

admin.site.register(models.User,UserAdmin)
admin.site.register(models.ProductTemp,ProductTempAdmin)
admin.site.register(models.InventoryMaterial,MaterialAdmin)
admin.site.register(models.OutStock,OutstockAdmin)
admin.site.register(models.Site)
admin.site.register(models.InStock,InstockAdmin)
admin.site.register(models.AutoLog,AutoLogAdmin)
admin.site.register(models.PreOutstock,PreOutstockAdmin)
admin.site.register(models.Uploadfiles,UploadfilesAdmin)
admin.site.site_url = '/index/'#修改admin中的viewsite的默认值