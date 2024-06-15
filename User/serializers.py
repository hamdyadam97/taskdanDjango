import uuid

from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from User.models import User


class SignupSerializer(serializers.ModelSerializer):
    is_update = False
    refresh = serializers.CharField(read_only=True, source='token')
    access = serializers.CharField(read_only=True, source='token.access_token')


    def validate_password(self, data):
        validate_password(data)
        return data


    def validate_email(self, data):
        users = User.objects.filter(email__iexact=data)

        if self.is_update:
            users.exclude(id=self.instance.id)

        if users.exists():
            raise serializers.ValidationError(_("This email address already exists."))
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('email', 'password', 'display_name', 'phone_number',
                  'refresh', 'access', 'is_email_verified', 'is_deactivated','is_notification_seen',
                  'is_phone_verified','phone_code','phone_country_code','is_superuser')
        extra_kwargs = {
            'password': {'write_only': True},
            'display_name': {'read_only': True},
            'phone_number': {'read_only': True},
            'is_email_verified': {'read_only': True},
            'is_deactivated': {'read_only': True},
            'phone_code': {'read_only': True},
            'is_phone_verified': {'read_only': True},
            'phone_country_code': {'read_only': True},
            'is_superuser': {'read_only': True},
            'is_notification_seen': {'read_only': True}
        }


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        try:
            super().validate(attrs)
        except AuthenticationFailed as ex:
            raise serializers.ValidationError(_("Incorrect email or password"))
        return SignupSerializer(instance=self.user, context=self.context).data


class EmailResendSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangeEmailVerifySerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    def create(self, validated_data):
        user = validated_data['user']
        code = validated_data['code']
        if code == user.verification_code:
            user.user.is_email_verified = True
            user.verification_code = None
            user.user.email = validated_data['email']
            user.changed = True
            user.user.save()
            user.save()
        else:
            raise serializers.ValidationError({'code': [_('Invalid code.')]})
        return validated_data


class UserSerializer(SignupSerializer):
    is_update = True

    class Meta:
        model = User
        fields = ('email', 'password', 'display_name', 'phone_number',
                  'refresh', 'access', 'is_email_verified', 'is_deactivated', 'is_notification_seen',
                  'is_phone_verified', 'phone_code', 'phone_country_code')
        extra_kwargs = {
            'is_email_verified': {'read_only': True},
            'date_joined': {'read_only': True},

        }

    def update(self, instance, attrs):
        return super().update(instance, attrs)



class EmailVerifySerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    def create(self, validated_data):
        user = validated_data['user']
        code = validated_data['code']
        if code == user.email_verification_code:
            user.is_email_verified = True
            user.email_verification_code = None
            user.save()
        else:
            raise serializers.ValidationError({'code': [_('Invalid code.')]})
        return validated_data


