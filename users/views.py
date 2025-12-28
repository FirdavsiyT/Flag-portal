from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db.models import Sum
from .models import User


@login_required
def profile(request):
    if request.method == 'POST':
        # (Оставляем ту же логику обработки форм, что обсуждали ранее, или упрощаем для старта)
        pass

    score = request.user.score
    flags_count = request.user.solve_set.count()

    # Расчет ранга
    # Считаем, сколько юзеров имеют больше очков
    users_above = User.objects.annotate(tp=Sum('solve__challenge__points')).filter(tp__gt=score).count()
    rank = users_above + 1

    context = {
        'score': score,
        'flags_count': flags_count,
        'rank': rank,
        'accuracy': '100%'  # Заглушка
    }
    return render(request, 'users/profile.html', context)