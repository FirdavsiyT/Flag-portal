from django.contrib import admin
from .models import Category, Challenge, Solve, Attempt

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'points', 'difficulty', 'max_attempts')
    list_filter = ('category', 'difficulty')
    search_fields = ('title', 'description')

@admin.register(Solve)
class SolveAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'date')
    list_filter = ('challenge__category', 'date')

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'flag_input', 'is_correct', 'timestamp')
    list_filter = ('is_correct', 'challenge')

admin.site.register(Category)