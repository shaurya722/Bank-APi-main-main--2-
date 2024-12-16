from django.urls import path

from api.views import LoginView, RegisterView
from django.urls import path
from .views import UserListCreateView, UserRetrieveUpdateDestroyView

urlpatterns = [
  
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
    # path('re/',BankView.as_view())
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
    
]
