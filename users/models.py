from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum


class User(AbstractUser):
    avatar_url = models.CharField(
        max_length=255,
        default="https://api.dicebear.com/7.x/bottts/svg?seed=default",
        verbose_name="Аватар"
    )

    @property
    def score(self):
        # Сумма очков за все решенные задачи
        # Используем related_name='solve_set' (стандартное) или 'solves' если определим в Solve
        total = self.solve_set.aggregate(total=Sum('challenge__points'))['total']
        return total if total is not None else 0

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"