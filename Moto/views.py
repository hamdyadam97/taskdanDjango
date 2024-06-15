from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum

from User.models import User
from .models import Moto

from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, F
from .models import Moto, User


class MotoStatsView(APIView):
    def get(self, request, *args, **kwargs):
        # Number of available motos
        available_motos = Moto.objects.aggregate(total_available=Sum('total'))['total_available'] or 0

        # Calculate the start of the current month
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Users registered this month
        users_registered_this_month = User.objects.filter(date_joined__gte=start_of_month)

        # Number of motos bought this month
        motos_bought_this_month = users_registered_this_month.aggregate(
            total_motos=Sum('account_moto')
        )['total_motos'] or 0

        # Total price of motos bought this month
        moto_count = Moto.objects.count()
        if moto_count > 0:
            total_moto_price = Moto.objects.aggregate(total_price=Sum(F('price') * F('total')))['total_price'] or 0
            moto_price = total_moto_price / moto_count
            total_price_this_month = motos_bought_this_month * moto_price
        else:
            total_price_this_month = 0

        data = {
            "available_motos": available_motos,
            "motos_bought_this_month": total_price_this_month,
            "total_price_this_month": total_price_this_month
        }
        return Response(data)
