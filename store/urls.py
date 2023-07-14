from django.urls import path

from . import views
from .views import user_logout

urlpatterns = [
	#Leave as empty string for base url
	path('store/', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
    path('category/<str:category_name>/', views.category_products, name='category_products'),
    

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    
	path('', views.user_login, name="login"),
    path('register/', views.user_register, name="register"),
    path('logout/', user_logout, name='logout'),
    
	path('search/', views.search, name="search"),
    
	path('view/', views.view, name="view"),
    

]