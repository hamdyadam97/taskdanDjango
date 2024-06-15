# serializers.py
from rest_framework import serializers
from .models import  Moto


class AtotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moto
        fields = ['id', 'name', 'price', 'created_at']
