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
from .permissions import IsLojista, IsCliente
from .fielters import Product_Filter, Review_Filter

class Category_Viewsets(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = Category_Serializer
    permission_classes = [IsLojista]
    http_method_names = ['get', 'post', 'put', 'patch']

class Product_Viewsets(viewsets.ModelViewSet):
    serializer_class = Product_Serializer
    permission_classes = [IsLojista]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    #filter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    
    search_fields = ['title', 'content']
    
    filterset_class = Product_Filter

    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        
        queryset = Product.objects.all().distinct()

        #para admins
        if user.is_staff:
            return queryset
        
        if getattr(user, 'usertype', None) == 'L':
            return queryset.filter(shopkeeper=user)

        return queryset.filter(active=True)
    
    def perform_create(self, serializer):
        serializer.save(shopkeeper=self.request.user)


class Stock_Viewsets(viewsets.ModelViewSet):
    permission_classes = [IsLojista]
    queryset = Stock.objects.all().order_by('amount')
    serializer_class = Stock_Serializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['amount', 'color_name']
    search_fields = ['amount', '=color_name', '=size']

    def get_queryset(self):
        return Stock.objects.filter(product=self.kwargs['product_pk'])
    
    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs['product_pk'])

class Review_Viewsets(viewsets.ModelViewSet):
    permission_classes = [IsCliente]
    serializer_class = Review_Serializer
    http_method_names = ['get', 'post']
    queryset = Review.objects.all()

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    
    search_fields = ['content']
    
    filterset_class = Review_Filter

    ordering_fields = ['star', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Review.objects.filter(product=self.kwargs['product_pk'])
    
    def perform_create(self, serializer):
        serializer.save(
            product_id=self.kwargs['product_pk'],
            user=self.request.user,
        )


class Contact_Support_email_viewset(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = contact_support_email.objects.all()
    serializer_class = Contact_Support_email_Serializer
    http_method_names = ['post']

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'contact_email'

    def create(self, request, *args, **kwargs):
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

        #envio do email
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
                        'menssage':
                        'Sua solicitação foi enviada.'
                    },
                    status=status.HTTP_200_OK,
                )
        
        except Exception as erro:
            return response.Response(
                status=status.HTTP_400_BAD_REQUEST
            )

class Cart_viewset(viewsets.ModelViewSet):
    permission_classes = [IsCliente, IsAuthenticated]
    serializer_class = Cart_Serializer
    http_method_names = ['get']

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Cart.objects.none()
        
        Cart.objects.get_or_create(user=user)
        
        return Cart.objects.filter(user=user)

    def list(self, request, *args, **kwargs):

        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    


class Cart_item_viewset(viewsets.ModelViewSet):
    permission_classes = [IsCliente, IsAuthenticated]
    serializer_class = Cart_item_Serializer
    http_method_names = ['post', 'put', 'delete']
    queryset = cart_item.objects.all()

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart_item.objects.filter(cart=cart)
    
    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)
    