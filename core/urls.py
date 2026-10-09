from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from transactions_app.admin_views import (
    activity_logs,
    daily_payment_summary,
    export_transactions_csv,
)

urlpatterns = [
    path(
        'admin/activity-logs/',
        activity_logs,
        name='admin_activity_logs',
    ),
    path(
        'admin/daily-payment-summary/',
        daily_payment_summary,
        name='daily_payment_summary',
    ),
    path(
        'admin/transactions/export-csv/',
        export_transactions_csv,
        name='admin_transaction_csv',
    ),
    path('admin/', admin.site.urls),

    path('auth/', include('users.urls')),
    path('cards/', include('cards.urls')),
    path('transactions/', include('transactions_app.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),

    path('', lambda request: redirect('card_list'), name='home'),
]
