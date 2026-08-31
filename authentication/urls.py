from django.urls import path
from .views import (
    GetUserOneView,
    GetUserView,
    LoginView,
    LogoutView,
    MyTokenObtainPairView,
    RegisterMember,
    RegisterView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register-member/', RegisterMember.as_view(), name='register_member'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair_jwt'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', GetUserView.as_view(), name='get_users'),
    path('users/<int:id>/', GetUserOneView.as_view(), name='get_user'),
]
