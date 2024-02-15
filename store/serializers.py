from rest_framework import serializers
from decimal import Decimal
from .models import Collection,Product,Review,Cart,CartItem,Customer,Order,OrderItem
from django.db import transaction

class CollectionSerializer(serializers.ModelSerializer):
      class Meta:
        model=Collection
        fields=['id', 'title','products_count']

      products_count=serializers.IntegerField(read_only=True)

class ProductSerializer(serializers.ModelSerializer):
      class Meta:
        model=Product
        fields=['id', 'title','slug','unit_price','inventory','description','price_with_tax','collection']
        
      price_with_tax=serializers.SerializerMethodField(method_name='calculate_price')  # this is how we add custom fields to our api response
      # collection=CollectionSerializer()    # second way of seriliazing the related field


      def calculate_price(self,product):
            return product.unit_price*Decimal(1.8)
      
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Review
        fields=['id' ,'name', 'description']

  # this is how we override the create method 
    def create(self, validated_data):
          product_id=self.context['product_id']
          return Review.objects.create(product_id=product_id,**validated_data)
    

class CartItemSerializer(serializers.ModelSerializer):
     product=ProductSerializer()
     total_price=serializers.SerializerMethodField()

     def get_total_price(self,cart_item:CartItem):
          return cart_item.quantity*cart_item.product.unit_price

     class Meta:
          model=CartItem
          fields=['id','quantity','product','total_price']

class CartSerializer(serializers.ModelSerializer):
     items= CartItemSerializer(many=True,read_only=True)
     items_price=serializers.SerializerMethodField()

     def get_items_price(self, cart_item:Cart):
          return sum([item.quantity*item.product.unit_price for item in cart_item.items.all()])
     class Meta:
          model=Cart
          fields=['id','items','items_price']


class AddCartItemSerializer(serializers.ModelSerializer):
     product_id=serializers.IntegerField()

     def validate_product_id(self, value):
          if not Product.objects.filter(pk=value).exists():
               raise serializers.ValidationError('Product with id is not found')
          return value

     def save(self, **kwargs):
          cart_id=self.context['cart_id']
          product_id=self.validated_data['product_id']
          quantity=self.validated_data['quantity']

          try:
               cart_item=CartItem.objects.get(cart_id=cart_id, product_id=product_id)
               cart_item.quantity+=quantity
               cart_item.save()
               self.instance=cart_item

          except CartItem.DoesNotExist:
               self.instance=CartItem.objects.create(cart_id=cart_id, **self.validated_data)

          return self.instance

     class Meta:
          model=CartItem
          fields=['id','product_id','quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
     
     class Meta:
          model=CartItem
          fields=['quantity'] 


class CustomerSerializer(serializers.ModelSerializer):
     user_id=serializers.IntegerField(read_only=True)
     class Meta:
          model=Customer
          fields=['id','user_id','birth_date','phone','membership']

class OrderItemSerializer(serializers.ModelSerializer):
     
     class Meta:
          model=OrderItem
          fields=['id','product','quantity','unit_price']


class OrderSerializer(serializers.ModelSerializer):
     items=OrderItemSerializer(many=True)
     class Meta:
        model=Order
        fields=['id','customer','payment_status','placed_at','items']


class UpdateOrderSerializer(serializers.ModelSerializer):
     class Meta:
          model = Order
          fields= ['payment_status']



class CreateOrderSerializer(serializers.Serializer):
      cart_id=serializers.IntegerField()

      def validate_cart_id(self, cart_id):
           if not Cart.objects.filter(pk=cart_id).exists():
                raise serializers.ValidationError('No Cart with the given id is exist')
           if not CartItem.objects.filter(cart_id=cart_id).count()==0:
                raise serializers.ValidationError('The cart is empty')
           return cart_id
           

      def save(self, **kwargs):
       with transaction.atomic():
          (customer,created)=Customer.objects.get_or_create(user_id=self.context['user_id']);
          order= Order.objects.create(customer=customer)

          cart_items=CartItem.objects.select_related('product').filter(cart_id=self.validated_data['cart_id'])
          order_items=[OrderItem(order=order,product=item.product,unit_price=item.product.unit_price,quantity=item.quantity) for item in cart_items]
          OrderItem.objects.bulk_create(order_items)

          Cart.objects.filter(pk=self.validated_data['cart_id']).delete()

          return order