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
    shopkeeper = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

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
            'shopkeeper',
            'created_at'
        ]
        extra_kwards = {
            'shopkeeper': {'write_only': False},
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
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'product',
            'content',
            'star',
            'created_at',
        ]
    
    def validate_star(self, value):
        if not (value>=0 and value<=5):
            raise serializers.ValidationError('Star: O valor deve estar entre 0 e 5.')
        
        return value

class Contact_Support_email_Serializer(serializers.ModelSerializer):
    class Meta:
        model = contact_support_email
        fields = [
           'email',
           'name',
           'subject',
           'content', 
        ]

    def validate_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError('Nome: Não deve conter números e caracteres especiais.')
        return value

    def validate_subject(self, value):
        if not len(value) <= 255:
            raise serializers.ValidationError('Assunto: Deve conter no máximo 255 caracteres')
        
        if not len(value) >= 15:
            raise serializers.ValidationError('Assunto: Deve conter no mínimo 15 caracteres')
        
        return value
    
    def validate_content(self, value):
        if not len(value) >= 250: 
            raise serializers.ValidationError('Conteudo: Deve conter no minimo 250 caracteres')
        
        if not len(value) <= 1500: 
            raise serializers.ValidationError('Conteudo: Deve conter no máximo 1500 caracteres')
        
        return value

class Cart_item_Serializer(serializers.ModelSerializer):
    product = Product_Serializer(many=False, read_only=True)
    variations = Stock_Serializer(many=False, read_only=True)

    # aceita apenas o id do produto
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    variations_id = serializers.PrimaryKeyRelatedField(
        queryset=Stock.objects.all(),
        source='variations',
        write_only=True,
    )
    
    subtotal = serializers.SerializerMethodField(method_name='sub_total')

    class Meta:
        model = cart_item
        fields = [
            'id',
            'product',
            'product_id',
            'variations',
            'variations_id',
            'amount',
            'subtotal'
        ]

    def sub_total(self,item:cart_item):
        return item.amount * item.product.price
    
    def validate_amount(self, value):
        if value <=0:
            raise serializers.ValidationError('Quantidade:  Deve ser maior que 0')
        return value
    
    def validate(self, attrs):
        
        product = attrs.get('product')
        variations = attrs.get('variations')
        cart = self.context['view'].get_cart()

        if product and not product.active:
            raise serializers.ValidationError('Produto: Não está disponível para compra.')
        
        if variations and product and variations.product_id != product.id:
            raise serializers.ValidationError('Variação:  Não pertence ao produto informado')
        
        if variations and attrs.get('amount', 1) > variations.amount:
            raise serializers.ValidationError(f'Estoque: Tem apenas {variations.amount} unidades disponivel.')

        if cart and product:
            existing_items = cart.item.exclude(product=product).select_related('product')
            for item in existing_items:
                if item.product.shopkeeper_id != product.shopkeeper_id:
                    raise serializers.ValidationError(f'Não pode adicionar produtos de lojistas diferentes \n No carrinho existe produtos do lojista {item.product.shopkeeper}')
                    

        return attrs

class Cart_Serializer(serializers.ModelSerializer):
    item = Cart_item_Serializer(many = True)
    total_price = serializers.SerializerMethodField(method_name='total')
    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'item',
            'total_price',
            'date_update'
        ]

    def total(self, cart:Cart):
        items = cart.item.all()
        total = sum( item.amount * item.product.price for item in items)
        return total
    
    
