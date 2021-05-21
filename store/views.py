from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
 
# Create your views here.

def store(request, category_slug = None):

    category = None
    products = None
    if category_slug != None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        page_product = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('-created_date')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        page_product = paginator.get_page(page)
        product_count = products.count()


    context = {
        'products' : page_product,
        'product_count' : product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):

    products = Product.objects.all().filter(is_available=True).order_by('-created_date')

    try:
        single_product = Product.objects.all().get(category__slug = category_slug, slug = product_slug, )
    except Exception as e:
        raise e

    context = {
        'single_product' : single_product,
        'products' : products,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()

    context = {
        'products' : products,
        'product_count' : product_count,
    }

    return render(request, 'store/store.html', context)