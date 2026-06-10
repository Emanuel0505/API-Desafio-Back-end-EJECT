from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action

from .models import *
from .serializers import *
from .permissions import IsLojista

class Category_Viewsets(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = Category_Serializer

class Product_Viewsets(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = Product_Serializer
    permission_classes = [IsLojista]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class Stock_Viewsets(viewsets.ModelViewSet):
    permission_classes = [IsLojista]
    queryset = Stock.objects.all()
    serializer_class = Stock_Serializer

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
  