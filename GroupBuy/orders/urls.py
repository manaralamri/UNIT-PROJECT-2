from django.urls import path
from .import views

app_name = 'orders'

urlpatterns = [
     path('create-order/<int:product_id>/', views.create_order_view, name='create_order_view'),
     path('create-group-purchase/<int:product_id>/', views.create_group_purchase, name='create_group_purchase'),
     path('group-purchase/<int:group_purchase_id>/', views.group_purchase_detail, name='group_purchase_detail'),
     path('join-group-purchase/<int:group_purchase_id>/', views.join_group_purchase, name='join_group_purchase'),
     path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
     path('group-purchases/', views.group_purchase_all, name='group_purchase_all'),
     path('existing/group/<int:product_id>/', views.existing_group_choices, name='existing_group_choices'),
     path('test/payment/<int:order_id>/', views.test_payment_view, name='test_payment_view')
]
