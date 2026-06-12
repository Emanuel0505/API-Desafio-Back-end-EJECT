from django.urls import path, include
from rest_framework_nested import routers
from .views import *

#Caminhos
router = routers.DefaultRouter()
router.register('category', Category_Viewsets, basename='Category')
router.register('product', Product_Viewsets, basename='Product')
# router.register('stock', Stock_Viewsets, basename='Stock')
router.register('review', Review_Viewsets, basename='Review')
router.register('address', Address_Viewsets, basename='Address')

router_contact = routers.DefaultRouter()
router_contact.register('email', Contact_Support_email_viewset,basename='email')

#Caminho aninhado de product
router_product = routers.NestedDefaultRouter(router, 'product', lookup = 'product')
router_product.register('variations', Stock_Viewsets, basename='stock-variations')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(router_product.urls)),
    path('contact/', include(router_contact.urls)),
    

]
