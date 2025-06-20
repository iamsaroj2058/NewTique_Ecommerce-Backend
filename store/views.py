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
from .models import Order, OrderItem
from .serializers import OrderSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import action


# ------------------ Product ViewSet ------------------
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        return queryset

    @action(detail=False, methods=["get"], url_path="stocks")
    def get_stocks(self, request):
        ids_param = request.GET.get("ids")
        if not ids_param:
            return Response({"error": "Missing ids parameter"}, status=400)

        try:
            ids = [
                int(id.strip()) for id in ids_param.split(",") if id.strip().isdigit()
            ]
            products = Product.objects.filter(id__in=ids)
            result = [{"id": p.id, "stock": p.stock} for p in products]
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# ------------------ Review ViewSet ------------------
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset.order_by("-created_at")  # Newest first

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsReviewAuthor()]
        return super().get_permissions()


class IsReviewAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


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

            return Response(
                {
                    "esewa_url": "https://rc-epay.esewa.com.np/api/epay/main/v2/form",
                    **payload,
                    "amount": str(amount),
                    "tax_amount": str(tax_amount),
                    "product_service_charge": "0",
                    "product_delivery_charge": "0",
                    "success_url": "http://localhost:8000/api/esewa-payment-success/",
                    "failure_url": "http://localhost:3000/payment-failure",
                    "signature": signature,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def generate_signature(self, data, secret_key):
        signed_fields = data["signed_field_names"].split(",")
        message = ",".join([f"{field}={data[field]}" for field in signed_fields])
        key = secret_key.encode("utf-8")
        message = message.encode("utf-8")
        hmac_sha256 = hmac.new(key, message, hashlib.sha256)
        return base64.b64encode(hmac_sha256.digest()).decode("utf-8")


@method_decorator(csrf_exempt, name="dispatch")
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

            return redirect(
                f"http://localhost:3000/payment-success?oid={oid}&amt={amt}&refId={refId}"
            )

        except Order.DoesNotExist:
            return redirect("http://localhost:3000/payment-failure")
        except Exception as e:
            print(f"Error: {str(e)}")
            return redirect("http://localhost:3000/payment-failure")


# store/views.py
class CashOnDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            data = request.data

            # Validate required fields
            required_fields = ["address", "products", "payment_method"]
            for field in required_fields:
                if field not in data:
                    return Response({"error": f"{field} is required"}, status=400)

            # Create order
            order = Order.objects.create(
                user=user,
                address=data["address"],
                total_price=0,  # Will be calculated below
                payment_method=data["payment_method"],
                transaction_uuid=str(uuid.uuid4()),
                status="Pending",
            )

            total_amount = Decimal("0")

            # Process each product
            for product_data in data["products"]:
                try:
                    product = Product.objects.get(id=product_data["id"])

                    # Validate stock
                    if product.stock < product_data["quantity"]:
                        order.delete()
                        return Response(
                            {"error": f"Not enough stock for {product.name}"},
                            status=400,
                        )

                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=product_data["quantity"],
                        price=product.price,
                    )

                    # Update total
                    total_amount += (
                        Decimal(str(product.price)) * product_data["quantity"]
                    )

                    # Reduce stock (only after payment would normally happen)
                    # product.stock -= product_data['quantity']
                    # product.save()

                except Product.DoesNotExist:
                    order.delete()
                    return Response(
                        {"error": f"Product with ID {product_data['id']} not found"},
                        status=404,
                    )

            # Update order total
            order.total_price = total_amount
            order.save()

            return Response(
                {
                    "message": "Order created successfully",
                    "order_id": order.id,
                    "total_amount": total_amount,
                },
                status=201,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=400)


@api_view(["GET"])
def get_product_stocks(request):
    ids_param = request.GET.get("ids")
    if not ids_param:
        return Response({"error": "Missing ids parameter"}, status=400)

    try:
        ids = [int(id.strip()) for id in ids_param.split(",") if id.strip().isdigit()]
        products = Product.objects.filter(id__in=ids)
        result = [{"id": p.id, "stock": p.stock} for p in products]
        return Response(result)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")
