from django.urls import path
from .import views

app_name = 'orders'

urlpatterns = [
    path('create-order/<int:product_id>/', views.create_order_view, name='create_order_view'),
    path('create-group-purchase/<int:product_id>/', views.create_group_purchase, name='create_group_purchase'),
    path('group-purchase/<int:group_purchase_id>/', views.group_purchase_detail, name='group_purchase_detail'),
    path('join-group-purchase/<int:group_purchase_id>/', views.join_group_purchase, name='join_group_purchase'),
    path('create-order-in-group/<int:group_purchase_id>/', views.create_order_in_group, name='create_order_in_group'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
]

#app_name='orders'
#urlpatterns = [
#  path('create/<int:product_id>/', views.create_order_view, name='create_order_view'),
#  path('create/group/<int:product_id>/', views.create_group_purchase, name='create_group_purchase'),
#  path('group/detail/<int:group_purchase_id>/', views.group_purchase_detail, name='group_purchase_detail'),
#  path('join/group/<int:group_purchase_id>/', views.join_group_purchase, name='join_group_purchase'),
#  path('create/order/group/<int:group_purchase_id>/', views.create_order_in_group, name='create_order_in_group'),
#  path('order/detail/<int:order_id>/', views.order_detail, name='order_detail'),
#
#
#   
#   
#   
#   
#   
#] 
