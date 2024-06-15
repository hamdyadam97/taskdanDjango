from django.urls import path
from .views import LoginView, SignupView, MeView, UserEmailVerifyView, DashboardView, UserListView

app_name ='User'
urlpatterns = [
    path('signup/', SignupView.as_view(),name='Signup'),
    path('login/', LoginView.as_view(),name='login'),
    path('email-verify/', UserEmailVerifyView.as_view(), name='email_verify'),
    path('me/', MeView.as_view(), name='me'),
    path('main/', DashboardView.as_view(), name='dashboard'),
    path('', UserListView.as_view(), name='user-list'),
]
