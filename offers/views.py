from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_control
from offers.models import CategoryOffer, ProductOffer
from userside.models import Category, Product
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
# Create your views here.


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def offers(request):
  category_offer = CategoryOffer.objects.all()
  product_offer = ProductOffer.objects.all()
  context = {
    'category_offer':category_offer,
    'product_offer' :product_offer
  }
  return render(request, 'offers.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category_offer_product(request, offer_slug, category=None):

  try:
    category_offer = get_object_or_404(CategoryOffer, category_offer_slug=offer_slug)
  except:
    return redirect('shop-product')

  category = category_offer.category

  if category:
    # category = category_offer.category.filter(is_available=True, slug = category)
    products = Product.objects.filter(category=category)
    paginator=Paginator(products,3)
    page=request.GET.get('page')
    paged_products=paginator.get_page(page)
    product_count=products.count()
    categories=[category]
    context={
          'products':paged_products,
          'product_count':product_count,
          'categories':categories,

      }
    return render(request, 'page-shop.html',context)
  else:
      products = Product.objects.filter(category=category)
      paginator=Paginator(products,3)
      page=request.GET.get('page')
      paged_products=paginator.get_page(page)
      product_count=products.count()
      categories=[category]

      context={
            'products':paged_products,
            'product_count':product_count,
            'categories':categories,

        }
      return render(request, 'page-shop.html',context)
  

  
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_offer_product(request, offer_slug):
  try:
    product_offer = get_object_or_404(ProductOffer, product_offer_slug=offer_slug)
  except:
    return redirect('shop-product')
  
  products = product_offer.product.filter(is_available=True)
  paginator=Paginator(products,3)
  page=request.GET.get('page')
  paged_products=paginator.get_page(page)
  product_count=products.count()
  categories = Category.objects.all()

  context = {
    'products':paged_products,
    'product_count':product_count,
    'categories':categories,

  }
  return render(request, 'page-shop.html',context)