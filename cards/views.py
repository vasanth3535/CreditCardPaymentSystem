from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Card


@login_required
def card_list(request):
    user_cards = Card.objects.filter(user=request.user)
    return render(
        request,
        'cards/card_list.html',
        {'cards': user_cards}
    )


@login_required
def add_card(request):
    if request.method == 'POST':
        name = request.POST.get('card_holder_name')
        card_type = request.POST.get('card_type')
        number = request.POST.get('card_number', '')
        expiry = request.POST.get('expiry_date')

        last_4 = number[-4:] if len(number) >= 4 else number
        masked_number = "**** **** **** " + last_4

        Card.objects.create(
            user=request.user,
            card_holder_name=name,
            card_type=card_type,
            masked_card_number=masked_number,
            last_four_digits=last_4,
            expiry_date=expiry
        )

        return redirect('card_list')

    return render(request, 'cards/add_card.html')


@login_required
def edit_card(request, card_id):
    card = Card.objects.get(
        id=card_id,
        user=request.user
    )

    if request.method == 'POST':
        card.card_holder_name = request.POST.get('card_holder_name')
        card.expiry_date = request.POST.get('expiry_date')
        card.save()

        return redirect('card_list')

    return render(
        request,
        'cards/edit_card.html',
        {'card': card}
    )


@login_required
def delete_card(request, card_id):
    card = Card.objects.get(
        id=card_id,
        user=request.user
    )
    card.delete()

    return redirect('card_list')
