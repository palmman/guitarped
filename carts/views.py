from django.shortcuts import render, redirect, get_object_or_404
from carts.models import CartItem, Cart
from store.models import Product
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) # get product
    if current_user.is_authenticated:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart by cart_id present the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, user=request.user)
            #if cart_item.quantity<cart_item.product.stock :
            cart_item.quantity+=1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                user=request.user,
                quantity=1
            )
            cart_item.save()

        return redirect('cart')

    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart by cart_id present the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            #if cart_item.quantity<cart_item.product.stock :
            cart_item.quantity+=1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )
            cart_item.save()

        return redirect('cart')


def cart(request, total=0, quantity=0, cart_item=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price)*(cart_item.quantity)
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
    }
    return render(request, 'store/cart.html', context)

def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity >1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.filter(product=product, user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

@login_required(login_url = 'login')
def checkout(request, total=0, quantity=0, cart_item=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
    }
    return render(request, 'store/checkout.html', context)

