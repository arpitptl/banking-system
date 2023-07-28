# accounts/urls.py

from django.urls import path
from .views import create_account, deposit, withdraw, transaction_history, create_bank, create_user, update_kyc_status

urlpatterns = [
    path('create_account/', create_account, name='create_account'),
    path('deposit/<int:account_id>/', deposit, name='deposit'),
    path('withdraw/<int:account_id>/', withdraw, name='withdraw'),
    path('transaction_history/<int:account_id>/', transaction_history, name='transaction_history'),
    path('create_user/', create_user, name='create_user'),
    path('create_bank/', create_bank, name='create_bank'),
    path('update_kyc/<int:account_id>/', update_kyc_status, name='update_kyc_status'),
]
