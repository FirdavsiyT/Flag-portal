from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from .models import Challenge, Category, Solve, Attempt
from users.models import User
import json
from collections import defaultdict


@login_required(login_url='/accounts/login/')
def dashboard(request):
    user_solves = Solve.objects.filter(user=request.user)
    owned_flags = user_solves.count()
    total_flags = Challenge.objects.count()

    # 1. Получаем глобальные решения (Успехи всех)
    solves_qs = Solve.objects.select_related('user', 'challenge', 'challenge__category').order_by('-date')[:20]

    # 2. Получаем ЛИЧНЫЕ провалы
    attempts_qs = Attempt.objects.filter(
        user=request.user,
        is_correct=False,
        challenge__max_attempts__gt=0
    ).select_related('challenge', 'challenge__category').order_by('timestamp')

    grouped_attempts = defaultdict(list)
    for att in attempts_qs:
        grouped_attempts[att.challenge_id].append(att)

    fail_events = []
    for ch_id, attempts in grouped_attempts.items():
        if not attempts: continue

        challenge = attempts[0].challenge
        limit = challenge.max_attempts

        if len(attempts) >= limit:
            locking_attempt = attempts[limit - 1]
            fail_events.append(locking_attempt)

    # 3. Объединяем списки
    activity_list = []

    for s in solves_qs:
        activity_list.append({
            'type': 'solve',
            'user': s.user,
            'challenge': s.challenge,
            'date': s.date,
            'sort_date': s.date
        })

    for f in fail_events:
        activity_list.append({
            'type': 'fail',
            'user': f.user,
            'challenge': f.challenge,
            'date': f.timestamp,
            'sort_date': f.timestamp
        })

    activity_log = sorted(activity_list, key=lambda x: x['sort_date'], reverse=True)[:10]

    context = {
        'owned_flags': owned_flags,
        'total_flags': total_flags,
        'activity_log': activity_log,
        'progress_percent': int((owned_flags / total_flags * 100)) if total_flags > 0 else 0
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='/accounts/login/')
def challenges_view(request):
    challenges = Challenge.objects.select_related('category').all()
    categories_qs = Category.objects.all()

    categories_data = {}
    for cat in categories_qs:
        icon = 'folder'

        categories_data[cat.name] = {
            'name': cat.name,
            'icon': icon
        }

    user_solves_ids = set(Solve.objects.filter(user=request.user).values_list('challenge_id', flat=True))

    user_attempts_map = {}
    attempts_qs = Attempt.objects.filter(user=request.user).values('challenge_id').annotate(count=Count('id'))
    for item in attempts_qs:
        user_attempts_map[item['challenge_id']] = item['count']

    challenges_data = []
    for c in challenges:
        # ИСПРАВЛЕНО: Добавляем avatar_url в список решивших
        solves_list = [{
            'user': s.user.username,
            'avatar': s.user.avatar_url,
            'date': s.date.strftime('%Y-%m-%d %H:%M')
        } for s in c.solves.select_related('user').order_by('-date')[:5]]

        is_solved = c.id in user_solves_ids
        attempts_count = user_attempts_map.get(c.id, 0)

        is_failed = False
        if c.max_attempts > 0 and attempts_count >= c.max_attempts and not is_solved:
            is_failed = True

        challenges_data.append({
            'id': c.id,
            'title': c.title,
            'category': c.category.name,
            'points': c.points,
            'difficulty': c.difficulty,
            'solved': is_solved,
            'failed': is_failed,
            'attempts': attempts_count,
            'max_attempts': c.max_attempts,
            'desc': c.description,
            'author': c.author,
            'solves': solves_list
        })

    context = {
        'categories': categories_qs,
        'categories_json': json.dumps(categories_data),
        'challenges_data': challenges_data
    }
    return render(request, 'challenges.html', context)


@login_required(login_url='/accounts/login/')
def scoreboard(request):
    users = User.objects.annotate(
        total_points=Sum('solves__challenge__points'),
        flags_count=Count('solves')
    ).order_by('-total_points', '-flags_count')[:50]

    leaderboard_data = []
    for index, u in enumerate(users, 1):
        leaderboard_data.append({
            'rank': index,
            'user': u.username,
            'points': u.total_points or 0,
            'solved': u.flags_count,
            'isMe': u == request.user,
            'avatar': u.avatar_url
        })

    context = {
        'leaderboard_data': leaderboard_data
    }
    return render(request, 'scoreboard.html', context)


@require_POST
@login_required
def submit_flag(request):
    try:
        data = json.loads(request.body)
        challenge_id = data.get('challenge_id')
        flag_input = data.get('flag')

        challenge = get_object_or_404(Challenge, id=challenge_id)

        attempts_count = Attempt.objects.filter(user=request.user, challenge=challenge).count()

        if challenge.max_attempts > 0 and attempts_count >= challenge.max_attempts:
            return JsonResponse(
                {'status': 'error', 'message': 'Max attempts reached! Task locked.', 'challenge_failed': True})

        if Solve.objects.filter(user=request.user, challenge=challenge).exists():
            return JsonResponse({'status': 'error', 'message': 'Already solved!'})

        is_correct = (flag_input == challenge.flag)

        Attempt.objects.create(
            user=request.user,
            challenge=challenge,
            flag_input=flag_input,
            is_correct=is_correct
        )

        if is_correct:
            Solve.objects.create(user=request.user, challenge=challenge)
            return JsonResponse({'status': 'success', 'message': 'Correct flag!'})
        else:
            new_attempts_count = attempts_count + 1
            challenge_failed = False
            message = 'Incorrect flag'

            if challenge.max_attempts > 0 and new_attempts_count >= challenge.max_attempts:
                challenge_failed = True
                message = 'Incorrect flag. Max attempts reached. Task locked.'

            return JsonResponse({
                'status': 'error',
                'message': message,
                'challenge_failed': challenge_failed
            })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)