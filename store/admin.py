from django.contrib import admin
from django.db.models.aggregates import Count
from django.utils.html import format_html,urlencode
from django.urls import reverse
from . import models


# to show custom filter
class InventoryFilter(admin.SimpleListFilter):
    title='inventory'
    parameter_name='inventory'

    def lookups(self, request, model_admin) :
        return [('<10','Low')]
    
    def queryset(self, request, queryset) :
        if self.value()=='<10':
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions=['clear_inventory']
    prepopulated_fields={ 
        'slug': ['title']
    }
    list_display=['title','unit_price','inventory_status','collection',]
    list_editable=['unit_price']
    list_per_page=10
    list_filter=['collection','last_update',InventoryFilter]
    search_fields=['title']
    

    def inventory_status(self,product):
        if product.inventory < 10:
            return 'LOW'
        return "Ok"
    
    @admin.action(description="Clear Inventory")
    def clear_inventory(self,request,queryset):
        updated_count=queryset.update(inventory=0)
        self.message_user(request,
                          f"{updated_count} were successfully updated"
                          )

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
     list_display=['title','products_count']
    
     def products_count(self,collection):
        url=(reverse('admin:store_product_changelist') + '?' + urlencode({
            "collection_id":str(collection.id)
            }))
        return format_html('<a href={}>{}</a>',url,collection.products_count)
         
     
     def get_queryset(self, request):
         return super().get_queryset(request).annotate(products_count=Count('product'))
    

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name',  'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )

class OrderItemInline(admin.TabularInline):
    model=models.OrderItem
    autocomplete_fields=['product']
    extra=0

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=['id','placed_at','customer']
    inlines=[OrderItemInline]
      

