from django.urls import  re_path
from .views import*

app_name='wallet'

urlpatterns = [
    re_path('balance/', GetBalance.as_view()),
    re_path('top-up/', TopUp.as_view()),
    # re_path('withdraw/', Withdraw.as_view()),
    re_path('wallet_topup_success/',WalletTopUpSuccess.as_view()),
    re_path('last7/<str:email>/',Last7Transactions.as_view()),
    re_path('wallet_details/',UserWalletDetails.as_view()),
    re_path('wallet_users/',SparkUsersView.as_view()),
    re_path('send-wallet-user/',SendToAccountView.as_view()),
    re_path('get-rates/',GetRates.as_view()),
    re_path('withdraw/',WithdrawView.as_view()),
    re_path('send-to-non/',SendNonSparkView.as_view()),
    re_path('check-pin/',CheckPINView.as_view()),
]
