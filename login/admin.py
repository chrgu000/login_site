# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import models
from django.contrib import admin
from django.utils.safestring import mark_safe
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display=('name','email','password')
    
class WarehouseAdmin(admin.ModelAdmin):
    list_display=('code','location','status','users')
    

class ProductAdmin(admin.ModelAdmin):
    list_display=('uniqueid','feature','description','count','purchase_price','sale_price','warehouse','user','image')




admin.site.register(models.User,UserAdmin)
admin.site.register(models.Warehouse,WarehouseAdmin)
admin.site.register(models.Product,ProductAdmin)

admin.site.site_url = '/index/'#修改admin中的viewsite的默认值