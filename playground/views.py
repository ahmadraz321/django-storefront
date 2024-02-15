from django.shortcuts import render
from django.db.models import Q,Value,Count,ExpressionWrapper,F,fields
from django.db.models.functions import Concat
from store.models import Product,OrderItem,Order,Customer,Collection


# Request handler View is 
def say_hello(request):

    # this will give products whose title contains coffee and it is case insensitive
    # products = Product.objects.filter(title__icontains='coffee')

    # this will give products whose inventory is less than 20 and also unit price is less than 20, In this query Django uses the SQL And Operator
    # products = Product.objects.filter(inventory__lt=20,unit_price__lt=20)

    # this will give products whose inventory is less than 20 or  unit price is less than 20, In this query Django uses the SQL OR Operator
    # products = Product.objects.filter(Q(inventory__lt=200)| Q(unit_price__lt=20))

    # this will run the order by query of SQL and give the sorted results by title in ascending order to make it descending add - as "-title"
    # products = Product.objects.order_by("title")

    # this will run the first product in ascending order of unit_price , also we have the latest method just like the earliest method that will return the first product in descending
    # product = Product.objects.earliest('unit_price')
 
    # to get the first 5 products we use the array slicing in method which will convert this to sql limit 
    # products = Product.objects.all()[0:5]

    # by default the above all gives us all the rows but what if I'm also interested in only the title of the product, but this will return the dictionary not the product object itself,to get the product instance itself we have a only method which give the product instance itself, we also have a defer method the row which added to the defer method means we query this in the later stage and the last collection__title means it will perform the inner join and look into the collection table and give me the title of the collection
    # products = Product.objects.values('title','unit_price','collection__title')

    #  to find products that are ordered;, here we check that which products ids are in the orderITem Table,
    # products=Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

    # Note that select_related() can only be used for foreign key and one-to-one relationships, whereas prefetch_related() can be used for many-to-one, many-to-many, and one-to-many relationships.
    # products=Product.objects.select_related('collection').all()
    # products=Product.objects.prefetch_related('promotions').all()

    # Find last five orders with the customer info
    # query_set=Order.objects.select_related('customer').order_by('-placed_at')[0:5]

    # Find the total number of Count this is aggregate in SQL like the count,sum,min,max here I'm using the count method;
    # count_object=Product.objects.aaggregate(count=Count('id'));

    # if we want to add another field to the Customer Table, we use the annotate object here we add the full_name, The Value object is used to add any value here I add the space  ;
    # full_name=Customer.objects.annotate(full_name=Concat('first_name',Value(' '), 'last_name'))

    # Using ExpressionWrapper to perform a mathematical operation
    # discount_price = Product.objects.annotate(discount_price=ExpressionWrapper(F('price') *0.8 , output_field=fields.DecimalField()))

    #  to insert a new record into the database
    # collection=Collection();
    # collection.title='Video Games'
    # collection.featured_product=Product(pk=1);
    # collection.save()


    #  to update  a record into the database
    # collection=Collection(pk=11);
    # collection.title='Games'
    # collection.featured_product=None
    # collection.save()
     
    # second way of updating a record
    # collection=Collection.objects.filter(pk=11).update(title='Video Games')

    # to delete a record
    # collection= Collection(pk=11);
    # collection.delete()

    # writing raw queries
    products=Product.objects.raw('select * from store_product')

    return render(request,'hello.html',{'products':list(products)})
  