from django.urls import path
from . import views
app_name = 'products'
urlpatterns = [
  path('create/', views.create_product_view, name='create_product_view'), 
  path('all/', views.all_product_view, name='all_product_view'),
  path('detail/<product_id>', views.product_detail_view, name='product_detail_view'),
  path('update/<product_id>', views.product_update_view, name="product_update_view"), 
  path('delete/<product_id>', views.product_delete_view, name="product_delete_view"), 
  path('review/add/<int:product_id>', views.add_review_view, name='add_review_view')



]
