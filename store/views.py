from django.db.models import Count
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import  IsAuthenticated,IsAdminUser
from .models import Product,Collection,OrderItem,Review,Cart,CartItem,Customer,Order
from .serializers import ProductSerializer, CollectionSerializer,ReviewSerializer,CartSerializer,CartItemSerializer,AddCartItemSerializer,UpdateCartItemSerializer,CustomerSerializer,OrderSerializer,CreateOrderSerializer,UpdateOrderSerializer
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly

# Serializer converts the model instance into a dictionary

class ProductViewSet(ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    filter_backends=[filters.DjangoFilterBackend, SearchFilter,OrderingFilter]
    filterset_fields = ['collection_id']
    search_fields= ['title', 'description']
    ordering_fields= ['unit_price']
    pagination_class=DefaultPagination
    permission_classes=[IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response({"error":"Product is not deleted as it is associated with the order item"},status=405)
        return super().destroy(request, *args, **kwargs)
          
# Collections Endpoints

class CollectionViewSet(ModelViewSet):
      queryset=Collection.objects.annotate(products_count=Count('product')).all()
      serializer_class=CollectionSerializer

      def destroy(self, request, *args, **kwargs):
          if Collection.objects.filter(product_set=kwargs['pk']).count() > 0:
              return Response({"error":"Product is not deleted as it is associated with the order item"},status=405)
          return super().destroy(request, *args, **kwargs)
      

# View Endpoints
class ReviewViewSet(ModelViewSet):
    serializer_class=ReviewSerializer

#    this is how we override the query set
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

#    this is how we read the id of the product from the url query params
    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}
    

class CartViewSet(CreateModelMixin,RetrieveModelMixin,GenericViewSet,DestroyModelMixin):
    queryset=Cart.objects.prefetch_related('items__product').all()
    serializer_class=CartSerializer
    


class CartItemViewSet(ModelViewSet):
    http_method_names=['get','patch','delete','post']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')
    

class CustomerViewSet(CreateModelMixin,RetrieveModelMixin,GenericViewSet,DestroyModelMixin):
       queryset=Customer.objects.all()
       serializer_class=CustomerSerializer
       permission_classes = [IsAdminUser]

       @action(detail=False,methods=['GET',"PUT"],permission_classes = [IsAuthenticated])
       def me(self,request):
           (customer,created)=Customer.objects.get_or_create(user_id=request.user.id)
           if request.method == 'GET':
             serializer=CustomerSerializer(customer)
             return Response(serializer.data)
           elif request.method == 'PUT':
               serializer=CustomerSerializer(customer,data=request.data)
               serializer.is_valid(raise_exception=True)
               serializer.save()
               return Response(serializer.data)
    


class OrderViewSet(ModelViewSet):
      http_method_names=['get', 'patch','delete','head','options']
      
      def get_permissions(self):
          if self.request.method in ['PATCH', 'DELETE']:
              return [IsAdminUser()]
          return [IsAuthenticated()]
      
      

      def create(self, request, *args, **kwargs):
          serializer=CreateOrderSerializer(data=request.data,context={'user_id':self.request.user.id})
          serializer.is_valid(raise_exception=True)
          order=serializer.save()
          serializer=OrderSerializer(order)
          return Response(serializer.data)

      def get_serializer_class(self):
          if self.request.method=='POST':
              return CreateOrderSerializer
          if self.request.method=='PATCH':
              return UpdateOrderSerializer
          return OrderSerializer

      def get_queryset(self):
          if self.request.user.is_staff:
              return Order.objects.all()
          
          id=  Customer.objects.only('id').get_or_create(user_id=self.request.user.id);
          return Order.objects.filter(customer_id=id)
          
