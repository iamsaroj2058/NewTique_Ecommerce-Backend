from rest_framework import viewsets, permissions
from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer
from django.conf import settings
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import uuid
import hmac
import hashlib
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated



class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.request.query_params.get('product')
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class EsewaInitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        amount = data.get("amount")
        product_id = data.get("product_id")
        product_name = data.get("product_name")

        transaction_uuid = str(uuid.uuid4())
        product_code = "EPAYTEST"  # Use your actual code in production
        tax_amount = 10
        total_amount = float(amount) + tax_amount

        # Step: Generate Signature
        message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
        secret_key = "8gBm/:&EnhH.1/q"
        signature = self.generate_signature(secret_key, message)

        return Response({
            "esewa_url": "https://rc-epay.esewa.com.np/api/epay/main/v2/form",
            "amount": amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "transaction_uuid": transaction_uuid,
            "product_code": product_code,
            "product_service_charge": 0,
            "product_delivery_charge": 0,
            "success_url": "http://localhost:3000/payment-success",
            "failure_url": "http://localhost:3000/payment-failure",
            "signed_field_names": "total_amount,transaction_uuid,product_code",
            "signature": signature,
        })

    def generate_signature(self, key, message):
        key = key.encode("utf-8")
        message = message.encode("utf-8")
        hmac_sha256 = hmac.new(key, message, hashlib.sha256)
        digest = hmac_sha256.digest()
        return base64.b64encode(digest).decode("utf-8")

    # ------------------ Product ViewSet ------------------
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        return queryset

# ------------------ Review ViewSet ------------------
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.request.query_params.get('product')
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

