from django.urls import path
from pages import views as pages_views

app_name = 'pages'

urlpatterns = [
    # Pages
    path('', pages_views.dashboard, name='dashboard'),
    path('challenges/', pages_views.challenges_view, name='challenges'),
    path('scoreboard/', pages_views.scoreboard, name='scoreboard'),

    # API
    path('api/submit_flag/', pages_views.submit_flag, name='submit_flag'),
]