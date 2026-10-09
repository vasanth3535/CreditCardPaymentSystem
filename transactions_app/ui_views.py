from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Transaction


@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-created_at')

    status_filter = request.GET.get('status')
    amount_filter = request.GET.get('amount')
    date_filter = request.GET.get('date')

    if status_filter:
        transactions = transactions.filter(status=status_filter)

    if amount_filter:
        transactions = transactions.filter(amount=amount_filter)

    if date_filter:
        transactions = transactions.filter(created_at__date=date_filter)

    return render(
        request,
        'transactions/history.html',
        {
            'transactions': transactions,
            'selected_status': status_filter,
            'selected_amount': amount_filter,
            'selected_date': date_filter,
        }
    )


@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        user=request.user
    )

    return render(
        request,
        'transactions/detail.html',
        {'transaction': transaction}
    )
