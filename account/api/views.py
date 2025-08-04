from django.shortcuts import render
from rest_framework import viewsets, permissions
from ..serializers import *
from ..models import *
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from knox.models import AuthToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
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
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(request, email=email, password=password)
            if user:
                _, token = AuthToken.objects.create(user)
                return Response(
                    {
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "name": user.full_name,
                            "phone": str(user.phone),
                        },
                        "token": token,
                    }
                )
            else:
                return Response({"error": "Invalid credentials"}, status=401)
        else:
            return Response(serializer.errors, status=400)


class RegisterViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


class UserViewset(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(email=self.request.user.email)
        return queryset


class VerifyTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response(
                {"error": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        request.META["HTTP_AUTHORIZATION"] = f"Token {token}"

        user_auth_tuple = TokenAuthentication().authenticate(request)
        if user_auth_tuple is not None:
            user, _ = user_auth_tuple
            return Response(
                {
                    "valid": True,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.username,
                    },
                }
            )
        else:
            return Response(
                {"valid": False, "error": "Invalid or expired token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class ChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {"error": "New password and confirm password do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"success": "Password updated successfully."}, status=status.HTTP_200_OK
        )


class UserProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "full_name": user.full_name,
                "email": user.email,
                "phone": str(user.phone),
            }
        )

    def put(self, request):
        user = request.user
        data = request.data

        # You can add validation here as needed
        user.full_name = data.get("full_name", user.full_name)
        user.email = data.get("email", user.email)
        user.phone = data.get("phone", user.phone)
        user.save()

        return Response(
            {
                "full_name": user.full_name,
                "email": user.email,
                "phone": str(user.phone),
                "message": "Profile updated successfully",
            },
            status=status.HTTP_200_OK,
        )
