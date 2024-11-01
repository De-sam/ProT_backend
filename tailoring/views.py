# tailoring/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Measurement, MeasurementCategory, Design
from .serializers import MeasurementSerializer, DesignSerializer,TailorSerializer
from userauth.models import CustomUser

class AddMeasurementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, customer_id):
        tailor = request.user
        if tailor.role != CustomUser.TAILOR:
            return Response({"detail": "Only tailors can add measurements."}, status=status.HTTP_403_FORBIDDEN)

        try:
            customer = CustomUser.objects.get(customer_id=customer_id, role=CustomUser.CUSTOMER)
            if customer not in tailor.customers.all():
                return Response({"detail": "Customer not found in your list."}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Invalid customer ID."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MeasurementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer, category=serializer.validated_data['category'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerTailorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != CustomUser.CUSTOMER:
            return Response({"detail": "Only customers can view their tailors."}, status=status.HTTP_403_FORBIDDEN)

        # Get all tailors who have added this customer
        tailors = user.tailors.all()  # This retrieves tailors who added the customer
        serializer = TailorSerializer(tailors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateDesignView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tailor = request.user
        if tailor.role != CustomUser.TAILOR:
            return Response({"detail": "Only tailors can add designs."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = DesignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tailor=tailor)  # Automatically assign the tailor as the creator
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DesignListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == CustomUser.TAILOR:
            # Tailors can view only their own designs
            designs = Design.objects.filter(tailor=user)
        elif user.role == CustomUser.CUSTOMER:
            # Customers can view designs from tailors who have added them as customers
            tailor_ids = user.tailors.values_list('id', flat=True)
            designs = Design.objects.filter(tailor__id__in=tailor_ids)
        else:
            return Response({"detail": "Invalid user role."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DesignSerializer(designs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
