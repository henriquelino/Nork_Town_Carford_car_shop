from django.contrib import admin
from django.urls import path

from .views import CarCRUD, CustomerCRUD, CustomerDetailView, Home, SalesCRUD

# yapf: disable
urlpatterns = [
    path('', Home.as_view(), name='home'),

    # cars
    path('cars/', CarCRUD.as_view(), name='cars_crud'),

    # sales
    path('sales/', SalesCRUD.as_view(), name='sales_crud'),

    # customers
    path('customer/', CustomerCRUD.as_view(), name='customers_crud'),
    path('customer/detail/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),

]

admin.site.site_header = "Carford Car Shop"
admin.site.site_title = "Carford Car Shop Admin Portal"
admin.site.index_title = "Welcome! How many cars can you sell today?"
