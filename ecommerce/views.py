from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from rest_framework import viewsets, filters, response, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models import *
from .serializers import *
from .permissions import IsShopkeeper, IsCustomer
from .fielters import Product_Filter, Review_Filter

class Category_Viewsets(viewsets.ModelViewSet):
    """List and manage product categories for shopkeepers.

    Requires shopkeeper permissions. Supports category listing, creation, and
    partial updates for the catalog taxonomy used by products.
    """
    queryset = Category.objects.all()
    serializer_class = Category_Serializer
    permission_classes = [IsShopkeeper]
    http_method_names = ['get', 'post', 'put', 'patch']

class Product_Viewsets(viewsets.ModelViewSet):
    """Expose products with filtering, ordering, and shopkeeper ownership.

    Shopkeepers can create and manage products. Read access changes by role:
    admins see everything, shopkeepers see their own products, and customers
    see only active products.
    """
    serializer_class = Product_Serializer
    permission_classes = [IsShopkeeper]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    #filter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    
    search_fields = ['title', 'content']
    
    filterset_class = Product_Filter

    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return products according to the current user's role and ownership."""
        user = self.request.user
        
        queryset = Product.objects.all().distinct()

        # for admins
        if user.is_staff:
            return queryset
        
        if getattr(user, 'usertype', None) == 'L':
            return queryset.filter(shopkeeper=user)

        return queryset.filter(active=True)
    
    def perform_create(self, serializer):
        """Store the authenticated user as the product owner when creating it."""
        serializer.save(shopkeeper=self.request.user)


class Stock_Viewsets(viewsets.ModelViewSet):
    """Manage product stock variations for a specific product.

    Nested route under product. The queryset is limited to the ``product_pk``
    from the URL so stock items never leak across products.
    """
    permission_classes = [IsShopkeeper]
    queryset = Stock.objects.all().order_by('amount')
    serializer_class = Stock_Serializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['amount', 'color_name']
    search_fields = ['amount', '=color_name', '=size']

    def get_queryset(self):
        """Return only stock rows that belong to the nested product route."""
        if getattr(self, 'swagger_fake_view', False):
            return Stock.objects.none()

        product_pk = self.kwargs.get('product_pk')
        if not product_pk:
            return Stock.objects.none()

        return Stock.objects.filter(product=product_pk)
    
    def perform_create(self, serializer):
        """Attach the stock variation to the product from the nested URL."""
        serializer.save(product_id=self.kwargs['product_pk'])

class Review_Viewsets(viewsets.ModelViewSet):
    """Create and list product reviews for nested product routes.

    Nested under a specific product. Reviews are filtered by ``product_pk`` and
    automatically linked to the current user on creation.
    """
    permission_classes = [IsShopkeeper]
    serializer_class = Review_Serializer
    http_method_names = ['get', 'post']
    queryset = Review.objects.all()

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    
    search_fields = ['content']
    
    filterset_class = Review_Filter

    ordering_fields = ['star', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return only reviews that belong to the nested product."""
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()

        product_pk = self.kwargs.get('product_pk')
        if not product_pk:
            return Review.objects.none()

        return Review.objects.filter(product=product_pk)
    
    def perform_create(self, serializer):
        """Attach the nested product and current user to the review record."""
        serializer.save(
            product_id=self.kwargs['product_pk'],
            user=self.request.user,
        )


class Contact_Support_email_viewset(viewsets.ModelViewSet):
    """Accept contact requests and forward them to the support inbox.

    Public POST endpoint with throttling enabled. It stores the request and then
    sends the message to the configured support inbox address.
    """
    permission_classes = [AllowAny]
    queryset = contact_support_email.objects.all()
    serializer_class = Contact_Support_email_Serializer
    http_method_names = ['post']

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'contact_email'

    def create(self, request, *args, **kwargs):
        """Validate the payload, save it, and email the support team."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.perform_create(serializer)

        name = serializer.data['name']
        email = serializer.data['email']
        subject = serializer.data['subject']
        content = serializer.data['content']
        

        #template email
        context = {
            'name': name,
            'email':email,
            'content': content,
        }

        plain_message = strip_tags(render_to_string('message_template_contact_support_email.html', context))

        # send email
        try:
            send_mail(
                subject= subject,
                message= plain_message,
                from_email = settings.DEFAULT_FROM_EMAIL,
                recipient_list=['newstylesupport@newstyle.com'],
                fail_silently=False,
            )
            
            return response.Response(
                    {
                        'message':
                        'Your request has been sent.'
                    },
                    status=status.HTTP_200_OK,
                )
        
        except Exception as erro:
            return response.Response(
                status=status.HTTP_400_BAD_REQUEST
            )

class Cart_viewset(viewsets.ModelViewSet):
    """Expose the authenticated user's current cart.

    Read-only endpoint that always returns a single cart object for the current
    authenticated customer, creating it on demand when necessary.
    """
    permission_classes = [IsCustomer, IsAuthenticated]
    serializer_class = Cart_Serializer
    http_method_names = ['get']

    def get_queryset(self):
        """Return the current user's cart, creating one if it does not exist."""
        user = self.request.user

        if not user.is_authenticated:
            return Cart.objects.none()
        
        Cart.objects.get_or_create(user=user)
        
        return Cart.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        """Serialize and return the single cart object for the user."""

        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class Cart_item_viewset(viewsets.ModelViewSet):
    """Create, update, and delete items inside the authenticated cart.

    The nested item routes operate only on the current user's cart and the
    related product and variation identifiers.
    """
    permission_classes = [IsCustomer, IsAuthenticated]
    serializer_class = Cart_item_Serializer
    http_method_names = ['post', 'put', 'delete']
    queryset = cart_item.objects.all()

    def get_queryset(self):
        """Return only the cart items that belong to the current user's cart."""
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart_item.objects.filter(cart=cart)
    
    def perform_create(self, serializer):
        """Attach the authenticated user's cart before saving the item."""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)
    
class Order_viewset(viewsets.ModelViewSet):
    """Create and inspect orders for the authenticated customer.

    Customers can list and create their own orders. Staff can inspect all
    orders. A custom ``cancel`` action is available for pending orders.
    """
    permission_classes = [IsCustomer, IsAuthenticated]
    serializer_class = Order_Serializer
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        """Return all orders for staff or only the authenticated user's orders."""
        user = self.request.user
        # Admin sees everything, user sees only their orders
        if user.is_staff:
            return orders.objects.all()
        return orders.objects.filter(user=user)

    def perform_create(self, serializer):
        """Persist a new order and bind it to the authenticated user."""
        # User is taken from the request, not from the payload
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Cancel a pending order when the requester has permission."""
        order = self.get_object()
        if order.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'No permission to cancel this order.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if order.status not in ['pending']:
            return Response(
                {'detail': 'Only pending orders can be canceled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = 'canceled'
        order.save()
        return Response(self.get_serializer(order).data)

class Payment_viewset(viewsets.ModelViewSet):
    """Create and inspect payments linked to a nested order.

    Nested under order. The endpoint only exposes payments for the order id
    captured in the URL and automatically assigns that order on create.
    """
    permission_classes = [IsCustomer,IsAuthenticated]
    serializer_class = Payment_Serializer
    http_method_names = ['get', 'post', 'put', 'delete']
    
    def get_queryset(self):
        """Return only the payments associated with the nested order id."""
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()

        order_pk = self.kwargs.get('order_pk')
        if not order_pk:
            return Payment.objects.none()

        return Payment.objects.filter(order=order_pk)
    
    def perform_create(self, serializer):
        """Attach the payment to the order referenced by the nested URL."""
        serializer.save(order_id=self.kwargs['order_pk'])
