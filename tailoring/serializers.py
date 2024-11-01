# tailoring/serializers.py

from rest_framework import serializers
from .models import Measurement, MeasurementCategory, Design, Order
from userauth.models import CustomUser

# Tailor Serializer
class TailorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email']

# Measurement Category Serializer
class MeasurementCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementCategory
        fields = ['id', 'name', 'description']

# Measurement Serializer
class MeasurementSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Measurement
        fields = [
            'id', 'customer', 'date_taken', 'category', 'category_name', 
            'neck_circumference_cm', 'shoulder_width_cm', 'chest_bust_circumference_cm', 
            'waist_circumference_cm', 'hip_circumference_cm', 'arm_length_cm', 
            'upper_arm_circumference_cm', 'wrist_circumference_cm', 'inseam_length_cm', 
            'outseam_length_cm', 'thigh_circumference_cm', 'knee_circumference_cm', 
            'calf_circumference_cm', 'ankle_circumference_cm', 'total_height_cm',
            'bust_point_to_bust_point_cm', 'bust_point_to_waist_cm', 
            'back_waist_length_cm', 'front_waist_length_cm', 'underbust_circumference_cm', 
            'chest_width_cm', 'back_width_cm', 'sleeve_length_cm', 'crotch_depth_cm'
        ]
        read_only_fields = ['date_taken']

# Design Serializer
class DesignSerializer(serializers.ModelSerializer):
    tailor_name = serializers.CharField(source='tailor.first_name', read_only=True)

    class Meta:
        model = Design
        fields = ['id', 'name', 'description', 'price', 'image', 'tailor', 'tailor_name']
        extra_kwargs = {
            'tailor': {'write_only': True},
            'image': {'required': True}
        }

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.first_name', read_only=True)
    design_name = serializers.CharField(source='design.name', read_only=True)
    tailor_name = serializers.CharField(source='design.tailor.first_name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'design', 'design_name', 'tailor_name', 
            'order_date', 'amount', 'transaction_id', 'payment_status'
        ]
        read_only_fields = ['order_date', 'amount', 'transaction_id', 'payment_status']



