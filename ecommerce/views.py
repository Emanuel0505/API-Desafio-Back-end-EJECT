from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action

from .models import *
from .serializers import *
from .permissions import IsLojista
from .fielters import Product_Filter

class Category_Viewsets(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = Category_Serializer
    permission_classes = [IsLojista]
    http_method_names = ['get', 'post', 'put', 'patch']

class Product_Viewsets(viewsets.ModelViewSet):
    queryset = Product.objects.all().distinct()
    serializer_class = Product_Serializer
    permission_classes = [IsLojista]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    #filter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    
    search_fields = ['title', 'content']
    
    filterset_class = Product_Filter

    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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
    queryset = Review.objects.all()
    serializer_class = Review_Serializer

class Address_Viewsets(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = Address_Serializer
  