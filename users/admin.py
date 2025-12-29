from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    # Добавляем кастомные поля в форму редактирования
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'country', 'avatar_url')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('bio', 'country', 'avatar_url')}),
    )

    # Настраиваем отображение таблицы пользователей (только ник и баллы)
    list_display = ('username', 'get_score')

    def get_score(self, obj):
        return obj.score

    get_score.short_description = 'Score'


admin.site.register(User, CustomUserAdmin)