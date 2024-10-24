from django.urls import path
from . import views




urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('store/', views.store, name='store'),
    path('add_item/', views.add_item, name='add_item'),
    path('search_item/', views.search_item, name='search_item'),
    path('edit_item/<int:pk>/', views.edit_item, name='edit_item'),
    path('edit_user_profile/', views.edit_user_profile, name='edit_user_profile'),
    path('delete_item/<int:pk>/', views.delete_item, name='delete_item'),
    path('dispense/', views.dispense, name='dispense'),
    path('cart/', views.cart, name='cart'),
    # path('add_new_user/', views.add_new_user, name='add_new_user'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('receipt/', views.receipt, name='receipt'),
    path('update_cart_quantity/<int:pk>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('dispensing_log/', views.dispensing_log, name='dispensing_log'),
    path('reports/', views.reports, name='reports'),
    path('manage_customers/', views.manage_customers, name='manage_customers'),
    path('register_customers/', views.register_customers, name='register_customers'),
    path('customer_list/', views.customer_list, name='customer_list'),
    path('delete_customer/<int:pk>/', views.delete_customer, name='delete_customer'),
    path('edit_customer/<int:pk>/', views.edit_customer, name='edit_customer'),
    path('exp_date_alert/', views.exp_date_alert, name='exp_date_alert'),
    path('daily_sales/', views.daily_sales, name='daily_sales'),
    path('monthly_sales/', views.monthly_sales, name='monthly_sales'),
    path('wallet_details/<int:pk>/', views.wallet_details, name='wallet_details'),
    path('add_funds/<int:pk>/', views.add_funds, name='add_funds'),
    path('reset_wallet/<int:pk>/', views.reset_wallet, name='reset_wallet'),
    path('search_customer_items/<int:customer_id>/', views.search_customer_items, name='search_customer_items'),
    path('select_items/<int:pk>/', views.select_items, name='select_items'),
    path('customers_on_negative/', views.customers_on_negative, name='customers_on_negative'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('change_user_password/', views.change_user_password, name='change_user_password'),
]
