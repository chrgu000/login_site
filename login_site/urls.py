"""login_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include,static
from django.contrib import admin
from login import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', views.index),
    url(r'^login/', views.login),
    url(r'^register/', views.register),
    url(r'^logout/', views.logout),
    url(r'^captcha', include('captcha.urls')),
    url(r'^addproduct/',views.addproduct),
    
    url(r'^uploadproduct/',views.UploadproductView.as_view(),name='uploadproduct'),
    url(r'^inventory/',views.InventoryView.as_view(),name='inventory_list'),
    url(r'^searchtest/$',views.searchtest),
    url(r'^detail/(\d+)$',views.detail,name='detail-url'),
    url(r'^result/',views.search),
    
    # url(r'^search/',views.search,name='search'),
    
    # Downside is material stock in related
    # url(r'^inventorymaterial/',views.inventoryMaterial),
    url(r'^inventorymaterial/',views.InventoryMaterial.as_view(),name='im_list'),
    url(r'^inventorydetail/(\d+)$',views.inventoryDetail,name='inventoryDetail-url'),
    url(r'^inventoryinit/',views.Inventoryinit.as_view(),name='inventoryInit-url'),
    url(r'^instock/',views.inStock),
    url(r'^instockdetail/(\d+)$',views.inStockDetail,name='inStockDetail-url'),
    # url(r'^instockadd/',views.inStockAdd),
    url(r'^instockadd/',views.Instockadd.as_view(),name='instock_add'),
    url(r'^initem/',views.inItem),
    url(r'^matitem/',views.matItem),
    url(r'^uploadmaterial/',views.Uploadmaterial.as_view(),name='im_upload'),
    #Downside is product and its relationship with material
    url(r'^productlist/',views.Productlist.as_view(),name='pt_list'),
    url(r'^addproducttemp/',views.Addproducttemp.as_view(),name='add_pt'),
    url(r'^productdetail/(\d+)$',views.productDetail,name='productDetail-url'),
    #outstock
    url(r'^outstock/',views.outStock),
    url(r'^outstockdetail/(\d+)$',views.outStockDetail,name='outStockDetail-url'),
    url(r'^outstockadd/',views.Outstockadd.as_view(),name='outstock_add'),
    
    url(r'^outitem/',views.outItem),
    url(r'^preoutitem/',views.preOutItem),
    url(r'^uploadoutstock/',views.Uploadoutstock.as_view(),name='out_upload'),
    
    url(r'^uploadnewpro/',views.Uploadnewpro.as_view(),name='upload_newpro'),
    url(r'^changecurrency/',views.Changecurrency.as_view(),name='change_currency'),
    url(r'^error/',views.error),
    url(r'^errorloglist/',views.ErrorLogList.as_view(),name='error_log'),
    url(r'^rapidmatmodify/',views.Rapidmatmodify.as_view(),name='rapid_matmodify'),
    url(r'^uploadmatmodify/',views.Uploadmatmodify.as_view(),name='upload_matmodify'),
    url(r'^rapidpromodify/',views.Rapidpromodify.as_view(),name='rapid_promodify'),
    url(r'^uploadpromodify/',views.Uploadpromodify.as_view(),name='upload_promodify'),
    url(r'^preoutstocklist/',views.preOutstockList,name='pre_outstock_list'),
    url(r'^preoutstock/',views.PreOutstock.as_view(),name='pre_outstock'),
    url(r'^preoutstockdetail/(\d+)$',views.PreOutstockDetail.as_view(),name='pre_outstock_detail'),
    url(r'^pre2outstock/',views.pre2OutStock,name='pre_outstock'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
