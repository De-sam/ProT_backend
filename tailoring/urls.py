# tailoring/urls.py

from django.urls import path
from .views import (
    AddMeasurementView, DesignListView, CreateDesignView, CustomerTailorListView,
    OrderCreateView, OrderListView, OrderConfirmView
)

urlpatterns = [
    path('add-measurement/<str:customer_id>/', AddMeasurementView.as_view(), name='add_measurement'),
    path('designs/', DesignListView.as_view(), name='design_list'),
    path('customer/tailors/', CustomerTailorListView.as_view(), name='customer_tailor_list'),
    path('designs/add/', CreateDesignView.as_view(), name='add_design'),
    path('orders/create/<int:design_id>/', OrderCreateView.as_view(), name='create_order'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/confirm/<int:order_id>/', OrderConfirmView.as_view(), name='confirm_order'),
]
