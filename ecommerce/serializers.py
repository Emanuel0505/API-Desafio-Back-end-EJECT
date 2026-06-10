from rest_framework import serializers

from .models import *
from .validators import invalid_color_hexadecimal

class Category_Serializer(serializers.ModelSerializer):
    class Meta: 
        model = Category
        fields = ['id', 'name']

class Images_product_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Images_product
        fields = ['id', 'product', 'image']

class Product_Serializer(serializers.ModelSerializer):
    #campo para receber diversa imagens de uma vez
    upload_images = serializers.ListField(
        child=serializers.ImageField(
            allow_empty_file=False,
            use_url=False), 
            write_only=True,
        )
    images = Images_product_Serializer(many=True, read_only=True)


    active = serializers.BooleanField(default=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 
            'title', 
            'content', 
            'price', 
            'category', 
            'upload_images',
            'images',
            'active',
            'author',
            'created_at'
        ]
        extra_kwards = {
            'author': {'write_only': False},
            'created_at': {'write_only': False},
        }
    
    def validate_title(self, value):
        if not len(value)<150:
            raise serializers.ValidationError('Titulo: deve conter menos de 150 caracteres.') 
        return value
        
    def validate_price(self, value):
        if not value > 0.01: 
            raise serializers.ValidationError('Preço: Não pode ser negativo.')


    def create(self, validated_data):
        upload_images = validated_data.pop('upload_images')
        product = Product.objects.create(**validated_data)

        #salva as imagens no model de Images_product
        for image in upload_images:
            Images_product.objects.create(product=product, image=image)
        
        return product
    

class Stock_Serializer(serializers.ModelSerializer):
    
    class Meta:
        model = Stock
        fields = [
            'id',
            'amount',
            'color_name',
            'color_hexadecimal',
            'size',
        ]
        extra_kwargs = {
            'product': {'write_only': True}
        }

    def validate_color_name(self, value):

        if not value.isalpha():
            raise serializers.ValidationError('Color_name: Não deve conter números e caracteres especiais.')
        
        return value

    def validate_color_hexadecimal(self, value):
        
        if invalid_color_hexadecimal(value):
            raise serializers.ValidationError('Color_hexadecimal: Deve seguir o modelo #FFF ou #FFFFFF.')
        
        return value
    
    def validate_amount(self, value):
        
        if not value >= 0 :
            raise serializers.ValidationError('Amount: Não pode ser negativo.')
        
        return value
    
    def validate(self, attrs):
        product_id = self.context['view'].kwargs.get('product_pk')
        color_name = attrs.get('color_name', getattr(self.instance, 'color_name', None))
        size = attrs.get('size', getattr(self.instance, 'size', None))

        query = Stock.objects.filter(
            product_id=product_id,
            color_name=color_name.lower(),
            size=size.upper(),
        )

        variation_id = self.instance.id if self.instance else None

        # No PUT/PATCH, ignora o próprio registro
        if variation_id:
            query = query.exclude(id=variation_id)

        if query.exists():
            raise serializers.ValidationError(
                'Variação: Já existe um stock registrado com essa cor e tamanho neste produto'
            )

        return attrs
        
    
class Review_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class Address_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
