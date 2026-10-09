import csv

from django.contrib import admin
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import Transaction


def record_admin_activity(request, description):
    LogEntry.objects.create(
        user_id=request.user.pk,
        content_type=ContentType.objects.get_for_model(Transaction),
        object_id=None,
        object_repr=description,
        action_flag=CHANGE,
        change_message=description,
    )


@staff_member_required
def daily_payment_summary(request):
    today = timezone.localdate()
    transactions = Transaction.objects.filter(created_at__date=today)

    total_amount = transactions.aggregate(
        total=Sum("amount")
    )["total"] or 0

    record_admin_activity(request, "Viewed daily payment summary")

    context = {
        "report_date": today,
        "total_transactions": transactions.count(),
        "successful_payments": transactions.filter(status="SUCCESS").count(),
        "failed_payments": transactions.filter(status="FAILED").count(),
        "pending_payments": transactions.filter(status="PENDING").count(),
        "total_amount": total_amount,
    }

    return render(request, "admin/daily_payment_summary.html", context)


@staff_member_required
def export_transactions_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="transactions.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        "Transaction ID",
        "Reference",
        "Username",
        "Card Last Four Digits",
        "Amount",
        "Status",
        "Created At",
    ])

    transactions = Transaction.objects.select_related(
        "user", "card"
    ).order_by("-created_at")

    for transaction in transactions:
        writer.writerow([
            transaction.id,
            transaction.transaction_reference,
            transaction.user.username,
            transaction.card.last_four_digits,
            transaction.amount,
            transaction.status,
            transaction.created_at,
        ])

    record_admin_activity(request, "Exported transaction records to CSV")
    return response


@staff_member_required
def activity_logs(request):
    search_query = request.GET.get("q", "").strip()

    logs = LogEntry.objects.select_related(
        "user", "content_type"
    ).order_by("-action_time")

    if search_query:
        logs = logs.filter(
            Q(user__username__icontains=search_query)
            | Q(object_repr__icontains=search_query)
            | Q(change_message__icontains=search_query)
        )

    paginator = Paginator(logs, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = admin.site.each_context(request)
    context.update({
        "title": "Admin Activity Logs",
        "page_obj": page_obj,
        "search_query": search_query,
        "total_logs": paginator.count,
    })

    return render(request, "admin/activity_logs.html", context)
