from rest_framework import serializers

from account.serializers import Card_Serializer
from account.models import card 

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
    # field to receive multiple images at once
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
            raise serializers.ValidationError('Title: must have less than 150 characters.') 
        return value
        
    def validate_price(self, value):
        if not value > 0.01: 
            raise serializers.ValidationError('Price: Cannot be negative or zero.')


    def create(self, validated_data):
        upload_images = validated_data.pop('upload_images')
        product = Product.objects.create(**validated_data)

        # saves images to the Images_product model
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
            raise serializers.ValidationError('Color name: Should not contain numbers and special characters.')
        
        return value

    def validate_color_hexadecimal(self, value):
        
        if invalid_color_hexadecimal(value):
            raise serializers.ValidationError('Color hexadecimal: Must follow the pattern #FFF or #FFFFFF.')
        
        return value
    
    def validate_amount(self, value):
        
        if not value >= 0 :
            raise serializers.ValidationError('Amount: Cannot be negative.')
        
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

        # On PUT/PATCH, ignores the own record
        if variation_id:
            query = query.exclude(id=variation_id)

        if query.exists():
            raise serializers.ValidationError(
                'Variation: There is already a stock registered with this color and size for this product'
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
            raise serializers.ValidationError('Star: The value must be between 0 and 5.')
        
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
            raise serializers.ValidationError('Name: Should not contain numbers and special characters.')
        return value

    def validate_subject(self, value):
        if not len(value) <= 255:
            raise serializers.ValidationError('Subject: Must have a maximum of 255 characters')
        
        if not len(value) >= 15:
            raise serializers.ValidationError('Subject: Must have a minimum of 15 characters')
        
        return value
    
    def validate_content(self, value):
        if not len(value) >= 250: 
            raise serializers.ValidationError('Content: Must have a minimum of 250 characters')
        
        if not len(value) <= 1500: 
            raise serializers.ValidationError('Content: Must have a maximum of 1500 characters')
        
        return value

class Cart_item_Serializer(serializers.ModelSerializer):
    product = Product_Serializer(many=False, read_only=True)
    variations = Stock_Serializer(many=False, read_only=True)

    # accepts only the product id
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
            raise serializers.ValidationError('Amount: Must be greater than 0')
        return value
    
    def validate(self, attrs):
        
        product = attrs.get('product')
        variations = attrs.get('variations')
        cart = self.context['view'].get_cart()

        if product and not product.active:
            raise serializers.ValidationError('Product: Is not available for purchase.')
        
        if variations and product and variations.product_id != product.id:
            raise serializers.ValidationError('Variation: Does not belong to the informed product')
        
        if variations and attrs.get('amount', 1) > variations.amount:
            raise serializers.ValidationError(f'Stock: Only {variations.amount} units available.')

        if cart and product:
            existing_items = cart.item.exclude(product=product).select_related('product')
            for item in existing_items:
                if item.product.shopkeeper_id != product.shopkeeper_id:
                    raise serializers.ValidationError(f'Cannot add products from different shopkeepers. \n The cart contains products from shopkeeper {item.product.shopkeeper}')
                    

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

class Order_item_Serializer(serializers.ModelSerializer):
    product = Product_Serializer(many=False, read_only=True)
    variations = Stock_Serializer(many=False, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Order_item
        fields = [
            'id',
            'product',
            'variations',
            'amount',
            'price',
            'subtotal',
        ]

    def get_subtotal(self, item):
        return item.amount * item.price
    
class Payment_Serializer(serializers.ModelSerializer):
    Card = Card_Serializer(many=False, read_only=True)
    card_id = serializers.PrimaryKeyRelatedField(
        queryset=card.objects.all(),
        source='Card',
        write_only=True,
        required=False,
        allow_null=True
    )
    class Meta:
        model = Payment
        fields = [
            'id',
            'type',
            'Card',
            'card_id',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def validate(self, attrs):
        payment_type = attrs.get('type')
        card_obj = attrs.get('Card')

        if payment_type in ['credit_card', 'debit_card'] and not card_obj:
            raise serializers.ValidationError(
                {'card_id': 'Card is required for card payment.'}
            )

        if payment_type in ['pix', 'boleto'] and card_obj:
            raise serializers.ValidationError(
                {'card_id': 'PIX and Boleto should not have a card associated.'}
            )

        request = self.context.get('request')
        if card_obj and request and card_obj.user != request.user:
            raise serializers.ValidationError(
                {'card_id': 'Card does not belong to the user.'}
            )

        return attrs

class Order_Serializer(serializers.ModelSerializer):
    items = Order_item_Serializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    payment = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )
    # payment_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Payment.objects.all(),
    #     source='payment',
    #     write_only=True,
    #     required=True
    # )

    class Meta:
        model = orders
        fields = [
            'id',
            'user',
            'payment',
            'items',
            'cart_item_ids',
            'status',
            'total_price',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['status', 'total_price', 'user',]

    def validate_cart_item_ids(self, value):
        if not value:
            raise serializers.ValidationError('Select at least one item from the cart.')
        return value

    def validate_payment_id(self, value):
        # Ensures that the payment belongs to the user
        if value.user != self.context['request'].user:
            raise serializers.ValidationError('Payment: Does not belong to the user.')
        return value

    def create(self, validated_data):
        cart_item_ids = validated_data.pop('cart_item_ids')
        user = self.context['request'].user

        # Gets the items from the user's cart
        cart_items = cart_item.objects.filter(
            id__in=cart_item_ids,
            cart__user=user
        ).select_related('product', 'variations')

        if not cart_items.exists():
            raise serializers.ValidationError('No valid items found in the cart.')

        # Validates that products are active
        inactive = cart_items.filter(product__active=False)
        if inactive.exists():
            raise serializers.ValidationError(
                'There are inactive products in the cart.'
            )

        # Validates stock
        for item in cart_items:
            if item.amount > item.variations.amount:
                raise serializers.ValidationError(
                    f'Insufficient stock for {item.product.title} '
                    f'({item.variations.color_name}/{item.variations.size}). '
                    f'Available: {item.variations.amount}'
                )

        order = orders.objects.create(
            user=user,
            status='CREATED',
            total_price= sum(item.amount * item.product.price for item in cart_items)
        )

        for cart_item_obj in cart_items:
            order_item = Order_item.objects.create(
                order=order,
                product=cart_item_obj.product,
                variations=cart_item_obj.variations,
                amount=cart_item_obj.amount,
                price=cart_item_obj.product.price
            )
            
            cart_item_obj.variations.amount -= cart_item_obj.amount
            cart_item_obj.variations.save()

        # Removes from cart
        cart_items.delete()

        return order


