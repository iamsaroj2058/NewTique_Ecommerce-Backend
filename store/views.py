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
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Order
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny
from decimal import Decimal
from .models import Order
from .serializers import OrderSerializer




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
                "success_url": "http://localhost:8000/api/esewa-payment-success/",
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


@method_decorator(csrf_exempt, name='dispatch')
class EsewaPaymentSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        oid = request.GET.get("oid")
        amt = request.GET.get("amt")
        refId = request.GET.get("refId")

        try:
            amount_decimal = Decimal(amt)
            order = Order.objects.get(transaction_uuid=oid, amount=amount_decimal)
            order.is_paid = True
            order.payment_ref_id = refId
            order.status = "Paid"
            order.save()

            return redirect(f"http://localhost:3000/payment-success?oid={oid}&amt={amt}&refId={refId}")

        except Order.DoesNotExist:
            return redirect("http://localhost:3000/payment-failure")
        except Exception as e:
             print(f"Error: {str(e)}")
             return redirect("http://localhost:3000/payment-failure")




class CashOnDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            data = request.data

            print("Received data:", data)

            address = data.get("address")
            product_id = data.get("product_id")
            amount = data.get("amount")

            if not all([address, product_id, amount]):
                return Response({"error": "Address, product_id, and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

            product = Product.objects.get(id=product_id)
            amount_decimal = Decimal(str(amount))

            order = Order.objects.create(
                user=user,
                product=product,
                amount=amount_decimal,
                total_price=amount_decimal,
                address=address,
                payment_method="Cash on Delivery",
                transaction_uuid=str(uuid.uuid4()),
                status="pending"
            )

            return Response({"message": "Order placed successfully."}, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({"error": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')