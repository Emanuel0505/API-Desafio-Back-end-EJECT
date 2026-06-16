from django.urls import path, include
from rest_framework_nested import routers
from .views import *

# Default routes
router = routers.DefaultRouter()
router.register('category', Category_Viewsets, basename='Category')
router.register('product', Product_Viewsets, basename='Product')
router.register(r'cart/items', Cart_item_viewset, basename='Cart-item')
router.register('order', Order_viewset, basename='Order')

# Contact routes
router_contact = routers.DefaultRouter()
router_contact.register('email', Contact_Support_email_viewset,basename='email')

# Nested product routes
router_product = routers.NestedDefaultRouter(router, 'product', lookup = 'product')
router_product.register('variations', Stock_Viewsets, basename='stock-variations')
router_product.register('review', Review_Viewsets, basename='review')
 
# Order routes
router_order = routers.NestedDefaultRouter(router ,'order', lookup='order')
router_order.register('payment', Payment_viewset, basename='Payment')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(router_product.urls)),
    path('contact/', include(router_contact.urls)),
    path('', include(router_order.urls)),
    path('cart/', Cart_viewset.as_view({'get': 'list'}), name='Cart'),
    

]
