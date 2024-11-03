# tailoring/urls.py

from django.urls import path
from .views import (
    UserProfileView,
    AddMeasurementView,
    EditMeasurementView,
    CustomerTailorListView,
    CreateDesignView,
    DesignListView,
    OrderCreateView,
    OrderListView,
    OrderConfirmView,
    ReleaseFundsView,
    RefundFundsView,
)

urlpatterns = [
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('add-measurement/<str:customer_id>/', AddMeasurementView.as_view(), name='add_measurement'),
    path('edit-measurement/<int:measurement_id>/', EditMeasurementView.as_view(), name='edit_measurement'),
    path('customer/tailors/', CustomerTailorListView.as_view(), name='customer_tailor_list'),
    path('designs/add/', CreateDesignView.as_view(), name='add_design'),
    path('designs/', DesignListView.as_view(), name='design_list'),
    path('orders/create/<int:design_id>/', OrderCreateView.as_view(), name='create_order'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/confirm/<int:order_id>/', OrderConfirmView.as_view(), name='confirm_order'),
    path('orders/release-funds/<int:order_id>/', ReleaseFundsView.as_view(), name='release_funds'),
    path('orders/refund-funds/<int:order_id>/', RefundFundsView.as_view(), name='refund_funds'),
]
