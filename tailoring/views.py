# tailoring/views.py

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk.transaction import ApplicationNoOpTxn
from .models import Measurement, MeasurementCategory, Design, Order
from .serializers import MeasurementSerializer, DesignSerializer, TailorSerializer
from userauth.models import CustomUser

# Algorand client setup
ALGOD_ADDRESS = "http://localhost:4001"  # Adjust for sandbox
ALGOD_TOKEN = "a" * 64  # Sandbox token
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)
CREATOR_MNEMONIC = "reward abandon essence globe velvet leaf barely olympic margin wasp portion bonus fine call job typical vintage neutral dumb salute test lens render absorb axis"

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        user_profile = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "address": user.wallet_address,
            "role": user.role,
        }

        try:
            account_info = algod_client.account_info(user.wallet_address)
            balance = account_info.get("amount", 0) / 1_000_000
            user_profile["balance"] = balance

            if user.role == CustomUser.TAILOR:
                user_profile["tailor_specific_field"] = "Tailor details here"
            elif user.role == CustomUser.CUSTOMER:
                user_profile["customer_specific_field"] = "Customer details here"

            return Response(user_profile, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class EditMeasurementView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, measurement_id):
        tailor = request.user
        if tailor.role != CustomUser.TAILOR:
            return Response({"detail": "Only tailors can edit measurements."}, status=status.HTTP_403_FORBIDDEN)

        try:
            measurement = Measurement.objects.get(id=measurement_id)
        except Measurement.DoesNotExist:
            return Response({"detail": "Measurement not found."}, status=status.HTTP_404_NOT_FOUND)

        if measurement.customer not in tailor.customers.all():
            return Response({"detail": "You do not have permission to edit this customer's measurements."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MeasurementSerializer(measurement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

        tailors = user.tailors.all()
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
            serializer.save(tailor=tailor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DesignListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == CustomUser.TAILOR:
            designs = Design.objects.filter(tailor=user)
        elif user.role == CustomUser.CUSTOMER:
            tailor_ids = user.tailors.values_list('id', flat=True)
            designs = Design.objects.filter(tailor__id__in=tailor_ids)
        else:
            return Response({"detail": "Invalid user role."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DesignSerializer(designs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, design_id):
        customer = request.user
        if customer.role != CustomUser.CUSTOMER:
            return Response({"detail": "Only customers can place orders."}, status=status.HTTP_403_FORBIDDEN)

        design = get_object_or_404(Design, id=design_id)
        amount = design.price

        order = Order.objects.create(
            customer=customer,
            design=design,
            amount=amount,
            payment_status="PENDING"
        )

        return Response({
            "message": "Order created successfully.",
            "order_id": order.id,
            "amount": order.amount,
            "design": design.name,
            "tailor": design.tailor.first_name,
            "payment_status": order.payment_status,
        }, status=status.HTTP_201_CREATED)

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == CustomUser.CUSTOMER:
            orders = Order.objects.filter(customer=user)
        elif user.role == CustomUser.TAILOR:
            orders = Order.objects.filter(design__tailor=user)
        else:
            return Response({"detail": "Invalid user role."}, status=status.HTTP_400_BAD_REQUEST)

        orders_data = [
            {
                "order_id": order.id,
                "design_name": order.design.name,
                "customer_name": order.customer.first_name,
                "order_date": order.order_date,
                "amount": order.amount,
                "payment_status": order.payment_status,
                "transaction_id": order.transaction_id,
            }
            for order in orders
        ]
        return Response(orders_data, status=status.HTTP_200_OK)

class OrderConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        tailor = request.user
        if tailor.role != CustomUser.TAILOR:
            return Response({"detail": "Only tailors can confirm orders."}, status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(Order, id=order_id, design__tailor=tailor)
        order.payment_status = "CONFIRMED"
        order.save()

        return Response({"message": "Order confirmed successfully."}, status=status.HTTP_200_OK)

# New view for releasing funds
class ReleaseFundsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        customer = request.user
        if customer.role != CustomUser.CUSTOMER:
            return Response({"detail": "Only customers can release funds."}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = Order.objects.get(id=order_id, customer=customer)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            params = algod_client.suggested_params()
            app_args = ["release"]

            txn = ApplicationNoOpTxn(customer.wallet_address, params, order.escrow_address, app_args)
            signed_txn = txn.sign(mnemonic.to_private_key(customer.algorand_private_key))
            txid = algod_client.send_transaction(signed_txn)
            algod_client.status_after_block(txid)

            return Response({"message": "Funds released successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# New view for requesting a refund
class RefundFundsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        tailor = request.user
        if tailor.role != CustomUser.TAILOR:
            return Response({"detail": "Only tailors can request a refund."}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = Order.objects.get(id=order_id, design__tailor=tailor)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            params = algod_client.suggested_params()
            app_args = ["refund"]

            txn = ApplicationNoOpTxn(tailor.wallet_address, params, order.escrow_address, app_args)
            signed_txn = txn.sign(mnemonic.to_private_key(tailor.algorand_private_key))
            txid = algod_client.send_transaction(signed_txn)
            algod_client.status_after_block(txid)

            return Response({"message": "Refund processed successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
