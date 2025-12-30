import random
import uuid
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from pages.models import Category, Challenge, Solve, Attempt

User = get_user_model()


class Command(BaseCommand):
    help = 'Napolnyaet bazu dannyh feykovymi polzovatelyami i aktivnostyu'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database population...')

        # 1. Создаем категории, если их нет
        categories_names = ['Web', 'Crypto', 'Pwn', 'Forensics', 'Reverse', 'OSINT']
        cat_objs = []
        for name in categories_names:
            cat, created = Category.objects.get_or_create(name=name)
            cat_objs.append(cat)

        self.stdout.write(f'Categories check: {len(cat_objs)} exist.')

        # 2. Создаем задачи (Challenges), если их мало
        if Challenge.objects.count() < 10:
            self.stdout.write('Creating dummy challenges...')
            for i in range(25):
                cat = random.choice(cat_objs)
                points = random.choice([100, 200, 300, 400, 500])
                diff = 'Easy'
                if points > 200: diff = 'Medium'
                if points > 400: diff = 'Hard'

                Challenge.objects.get_or_create(
                    title=f'{cat.name} Quest {i + 1}',
                    defaults={
                        'category': cat,
                        'description': f'This is a generated challenge for {cat.name}. Find the flag!',
                        'points': points,
                        'difficulty': diff,
                        'flag': f'CTF{{fake_flag_{i}_{uuid.uuid4().hex[:4]}}}',
                        'max_attempts': 0
                    }
                )

        challenges = list(Challenge.objects.all())
        self.stdout.write(f'Challenges available: {len(challenges)}')

        # 3. Генерируем пользователей и активность
        self.stdout.write('Generating users and activity logs...')

        usernames_base = [
            'Neo', 'Morpheus', 'Trinity', 'Cipher', 'Tank', 'Dozer', 'Mouse', 'Switch', 'Apoc',
            'Smith', 'Brown', 'Jones', 'Oracle', 'Seraph', 'Merovingian', 'Persephone',
            'Keymaker', 'Architect', 'Ghost', 'Niobe', 'Lock', 'Sora', 'Freya', 'Bane',
            'Axel', 'Maggie', 'Kali', 'Sparks', 'Vector', 'Binary', 'Hex', 'Glitch', 'Daemon',
            'Root', 'Admin', 'User', 'Guest', 'System', 'Null', 'Void', 'Shadow', 'Phantom',
            'Cyber', 'Punk', 'Net', 'Runner', 'Blade', 'Zero', 'Cool', 'Hacker'
        ]

        # Время старта "соревнований" (48 часов назад)
        start_time = timezone.now() - timedelta(hours=48)

        created_users_count = 0

        for i in range(50):  # Создаем 50 пользователей
            # Генерация уникального имени
            base = random.choice(usernames_base)
            suffix = str(random.randint(100, 9999))
            username = f"{base}_{suffix}"

            if User.objects.filter(username=username).exists():
                continue

            # Создание пользователя
            user = User.objects.create_user(
                username=username,
                email=f"{username.lower()}@hacklabs.local",
                password='password123'
            )
            created_users_count += 1

            # Установка случайного аватара
            # Используем те же сиды, что и в вашем шаблоне для разнообразия
            seeds = ['Felix', 'Aneka', 'Zack', 'Midnight', 'Shadow', 'Cyber', 'Glitch', 'Neo', 'Flux', 'Echo', 'Byte',
                     'Pixel', 'Vortex', 'Spark', 'Nova']
            seed = random.choice(seeds) + str(random.randint(1, 100))
            user.avatar_url = f"https://api.dicebear.com/7.x/bottts/svg?seed={seed}"
            user.save()

            # Имитация решений (Solves)
            # Каждый юзер решает от 0 до 15 задач
            num_solves = random.randint(0, 15)
            solved_challenges = random.sample(challenges, num_solves) if num_solves <= len(challenges) else challenges

            # Имитируем, что пользователь решал задачи в разное время
            current_user_time = start_time + timedelta(minutes=random.randint(0, 600))  # Случайный старт

            for challenge in solved_challenges:
                # Шаг времени вперед (от 10 мин до 3 часов на задачу)
                current_user_time += timedelta(minutes=random.randint(10, 180))

                if current_user_time > timezone.now():
                    break

                # Создаем решение
                # Важно: для полей auto_now_add нужно сохранять объект, а потом обновлять дату
                solve = Solve.objects.create(
                    user=user,
                    challenge=challenge
                )
                solve.date = current_user_time
                solve.save(update_fields=['date'])

                # Создаем успешную попытку (для логов)
                att = Attempt.objects.create(
                    user=user,
                    challenge=challenge,
                    flag_input=challenge.flag,
                    is_correct=True
                )
                att.timestamp = current_user_time
                att.save(update_fields=['timestamp'])

            # Имитация ошибок (Failures)
            # 20% шанс, что у пользователя будут ошибки
            if random.random() < 0.2:
                num_fails = random.randint(1, 5)
                for _ in range(num_fails):
                    ch = random.choice(challenges)
                    fail_time = start_time + timedelta(minutes=random.randint(0, 2800))

                    if fail_time > timezone.now():
                        continue

                    att = Attempt.objects.create(
                        user=user,
                        challenge=ch,
                        flag_input='CTF{wrong_flag}',
                        is_correct=False
                    )
                    att.timestamp = fail_time
                    att.save(update_fields=['timestamp'])

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_users_count} users with activity!'))