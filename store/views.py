from rest_framework import viewsets, permissions
from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import uuid


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


@api_view(['POST'])
def get_esewa_payment_data(request):
    amount = request.data.get('amount', 0)
    pid = str(uuid.uuid4())

    return Response({
        'amt': amount,
        'pdc': 0,
        'psc': 0,
        'txAmt': 0,
        'tAmt': amount,
        'pid': pid,
        'scd': settings.ESEWA_MERCHANT_ID,
        'su': settings.ESEWA_SUCCESS_URL,
        'fu': settings.ESEWA_FAILURE_URL,
        'payment_url': settings.ESEWA_PAYMENT_URL,
    })


@api_view(['GET'])
def verify_esewa_payment(request):
    ref_id = request.GET.get('refId')
    pid = request.GET.get('pid')
    amt = request.GET.get('amt')

    payload = {
        'amt': amt,
        'rid': ref_id,
        'pid': pid,
        'scd': settings.ESEWA_MERCHANT_ID,
    }

    response = requests.post(settings.ESEWA_VERIFY_URL, data=payload)
    if response.status_code == 200 and "Success" in response.text:
        return Response({'message': 'Payment Verified Successfully', 'success': True})
    else:
        return Response({'message': 'Payment Verification Failed', 'success': False})
