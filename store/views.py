from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
import uuid
import hmac
import hashlib
import base64

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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.request.query_params.get('product')
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ------------------ Esewa Payment Initiation ------------------
class EsewaInitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            product_code = settings.ESEWA_MERCHANT_CODE
            secret_key = settings.ESEWA_SECRET_KEY

            data = request.data
            amount = float(data.get("amount"))
            tax_amount = 10
            total_amount = amount + tax_amount
            transaction_uuid = str(uuid.uuid4())

            payload = {
                "total_amount": str(total_amount),
                "transaction_uuid": transaction_uuid,
                "product_code": product_code,
                "signed_field_names": "total_amount,transaction_uuid,product_code",
            }

            signature = self.generate_signature(payload, secret_key)

            return Response({
                "esewa_url": "https://rc-epay.esewa.com.np/api/epay/main/v2/form",
                **payload,
                "amount": str(amount),
                "tax_amount": str(tax_amount),
                "product_service_charge": "0",
                "product_delivery_charge": "0",
                "success_url": "http://localhost:3000/payment-success",
                "failure_url": "http://localhost:3000/payment-failure",
                "signature": signature,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def generate_signature(self, data, secret_key):
        signed_fields = data["signed_field_names"].split(",")
        message = ",".join([f"{field}={data[field]}" for field in signed_fields])
        key = secret_key.encode("utf-8")
        message = message.encode("utf-8")
        hmac_sha256 = hmac.new(key, message, hashlib.sha256)
        return base64.b64encode(hmac_sha256.digest()).decode("utf-8")
