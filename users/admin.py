from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Расширяем стандартную админку пользователя, чтобы видеть новые поля
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('avatar_url', 'bio', 'country')}),
    )