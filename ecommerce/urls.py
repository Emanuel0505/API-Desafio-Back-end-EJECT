from django.urls import path, include
from rest_framework_nested import routers
from .views import *

#Caminhos padrão
router = routers.DefaultRouter()
router.register('category', Category_Viewsets, basename='Category')
router.register('product', Product_Viewsets, basename='Product')
#router.register('review', Review_Viewsets, basename='Review')

#caminhos de contact
router_contact = routers.DefaultRouter()
router_contact.register('email', Contact_Support_email_viewset,basename='email')

#Caminho aninhado de product
router_product = routers.NestedDefaultRouter(router, 'product', lookup = 'product')
router_product.register('variations', Stock_Viewsets, basename='stock-variations')
router_product.register('review', Review_Viewsets, basename='review')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(router_product.urls)),
    path('contact/', include(router_contact.urls)),
    

]
