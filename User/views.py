from django.db.models import Sum, F
from django.shortcuts import render
from django.utils.decorators import method_decorator
from drf_yasg.openapi import Parameter, IN_QUERY
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from Moto.models import Moto
from User import serializers
from User.models import User
from User.serializers import SignupSerializer, LoginSerializer, UserSerializer


# Create your views here.
@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description="""
    This endpoint is used to signup a new user.
    NOTE: to upload the image you need to pass it as a avatar parameter with the data
    """,
    manual_parameters=[
        Parameter('avatar', IN_QUERY,
                  'you can upload your image here',
                  type='file')
    ],
))
class SignupView(CreateAPIView):
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(email__iexact=request.data.get('email', ''))

        return self.create(request, *args, **kwargs)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class MeView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        me = self.serializer_class(self.request.user, data=self.request.data,
                                   context=self.get_serializer_context(), partial=True)
        me.is_valid(raise_exception=True)
        me.update(self.request.user, me.validated_data)

        return Response(self.serializer_class(self.request.user).data)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)


@method_decorator(name='post', decorator=swagger_auto_schema(
    responses={
        201: serializers.SignupSerializer()
    },
))
class UserEmailVerifyView(CreateAPIView):
    serializer_class = serializers.EmailVerifySerializer

    def perform_create(self, serializer):
        user = User.objects.filter(email=serializer.validated_data['email']).last()
        if not user:
            raise serializers.serializers.ValidationError({'email': [('Invalid email.')]})

        return serializer.save(user=user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        result = serializers.SignupSerializer(user['user']).data
        return Response(result, status=status.HTTP_201_CREATED, headers=headers)



class DashboardView(APIView):
    permission_classes = [IsAdminUser]


    def get(self, request, *args, **kwargs):
        total_users = User.objects.count()
        users_with_motos = User.objects.filter(account_moto__isnull=False).count()
        total_moto_data = Moto.objects.aggregate(
            total_count=Sum('total'),
            total_price=Sum(F('total') * F('price'))
        )
        total_moto_count = total_moto_data['total_count']
        total_moto_price = total_moto_data['total_price']

        data = {
            "total_users": total_users,
            "users_with_motos": users_with_motos,
            "total_moto_count": total_moto_count,
            "total_moto_price": total_moto_price
        }
        return Response(data)

class UserListView(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)