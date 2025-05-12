from django.shortcuts import render
from rest_framework import viewsets, permissions 
from ..serializers import * 
from ..models import * 
from rest_framework.response import Response 
from django.contrib.auth import get_user_model, authenticate
from knox.models import AuthToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from knox.auth import TokenAuthentication
from rest_framework.authentication import get_authorization_header
from rest_framework import status

User = get_user_model()

class LoginViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request): 
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(): 
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user: 
                _, token = AuthToken.objects.create(user)
                return Response(
                    {
                        "user": self.serializer_class(user).data,
                        "token": token
                    }
                )
            else: 
                return Response({"error":"Invalid credentials"}, status=401)    
        else: 
            return Response(serializer.errors,status=400)



class RegisterViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else: 
            return Response(serializer.errors,status=400)


class UserViewset(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def get_queryset(self):
        queryset= self.queryset.filter(email=self.request.user.email) 
        return queryset
    

class VerifyTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST)

        request.META['HTTP_AUTHORIZATION'] = f"Token {token}"

        user_auth_tuple = TokenAuthentication().authenticate(request)
        if user_auth_tuple is not None:
            user, _ = user_auth_tuple
            return Response({
                "valid": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.username,
                }
            })
        else:
            return Response({"valid": False, "error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)
