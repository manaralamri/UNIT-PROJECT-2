from django.urls import path
from . import views
app_name = 'products'
urlpatterns = [
  path('create/', views.create_product_view, name='create_product_view'), 
  path('all/', views.all_product_view, name='all_product_view'),
  path('detail/<product_id>', views.product_detail_view, name='product_detail_view'),
  path('update/<product_id>', views.product_update_view, name="product_update_view"), 
  path('delete/<product_id>', views.product_delete_view, name="product_delete_view"), 
  path("search/", views.search_products_view, name="search_products_view"),
  path('review/add/<int:product_id>', views.add_review_view, name='add_review_view'),
  path('toggle-favorite/<int:product_id>/', views.toggle_favorite_view, name='toggle_favorite_view'),
  path('favorites/', views.favorite_products_view, name='favorite_products_view'),
  path('cart/', views.cart_view, name='cart_view'), 
  path('add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart_view'),  # لإضافة منتج للسلة
  path('remove/<int:product_id>/', views.remove_from_cart_view, name='remove_from_cart_view'),  # لإزالة منتج من السلة
  path('cart/increase/<int:product_id>/', views.increase_cart_quantity_view, name='increase_cart_quantity_view'),
  path('cart/decrease/<int:product_id>/', views.decrease_cart_quantity_view, name='decrease_cart_quantity_view'),







]
