# tailoring/urls.py
from django.urls import path
from .views import AddMeasurementView, DesignListView, CreateDesignView,CustomerTailorListView

urlpatterns = [
    path('add-measurement/<str:customer_id>/', AddMeasurementView.as_view(), name='add_measurement'),
    path('designs/', DesignListView.as_view(), name='design_list'),  # List designs
    path('customer/tailors/', CustomerTailorListView.as_view(), name='customer_tailor_list'),
    path('designs/add/', CreateDesignView.as_view(), name='add_design'),  # Add a new design
]
