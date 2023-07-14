from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.forms import UserCreationForm
from .forms import OrderForm, CreateUserForm, SearchForm, LoginForm, RegistrationForm
from .models import Product
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

def category_products(request, category_name):
    products = Product.objects.filter(category=category_name)
    context = {'products': products}
    return render(request, 'store/category_products.html', context)



def user_logout(request):
    logout(request)
    return redirect('login')

def view(request):
	thisProduct = Product.name
	return render(request, 'store/view.html', {})



def search(request, category_name=None):
    form = SearchForm(request.GET)
    results = []

    if form.is_valid():
        name = form.cleaned_data['name']
        min_price = form.cleaned_data['min_price']
        max_price = form.cleaned_data['max_price']
        alphabet = form.cleaned_data['alphabet']  # Extract the alphabet field

        # Perform the search based on the provided criteria
        queryset = Product.objects.all()

        if name:
            queryset = queryset.filter(name__icontains=name)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if alphabet:  # Add filtering by alphabet
            queryset = queryset.filter(name__istartswith=alphabet)

        # Filter by category if specified
        if category_name:
            queryset = queryset.filter(category=category_name)

        results = queryset.order_by('name')

    context = {'results': results, 'form': form}
    return render(request, 'search.html', context)






def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('store') 
    else:
        form = LoginForm()
    return render(request, 'store/login.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store')  
    else:
        form = RegistrationForm()
    return render(request, 'store/register.html', {'form': form})



def store(request):
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.all()

    if search_query:
        products = products.filter(name__icontains=search_query)

    if min_price and max_price:
        products = products.filter(price__range=(min_price, max_price))
    elif min_price:
        products = products.filter(price__gte=min_price)
    elif max_price:
        products = products.filter(price__lte=max_price)

    paginator = Paginator(products, 9)  # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'products': page_obj, 'search_query': search_query}
    return render(request, 'store/store.html', context)



def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == float(order.get_cart_total):
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)