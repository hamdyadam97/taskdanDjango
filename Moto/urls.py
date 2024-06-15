from Moto.views import MotoStatsView
from django.urls import path


app_name ='Moto'
urlpatterns = [
    path('moto-stats/', MotoStatsView.as_view(), name='moto-stats'),
]
