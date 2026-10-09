from django.urls import path

from .payment_views import make_payment
from .ui_views import transaction_detail, transaction_history
from .views import TransactionDetailView, TransactionListView


urlpatterns = [
    path('payment/', make_payment, name='make_payment'),
    path('history/', transaction_history, name='transaction_history'),
    path(
        'history/<int:transaction_id>/',
        transaction_detail,
        name='transaction_detail_ui'
    ),
    path('', TransactionListView.as_view(), name='transaction_list'),
    path(
        '<int:pk>/',
        TransactionDetailView.as_view(),
        name='transaction_detail'
    ),
]
