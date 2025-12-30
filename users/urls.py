from django.urls import path
from users import views as users_views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', users_views.register, name='register'),
    path('avatar-setup/', users_views.avatar_setup, name='avatar_setup'),
    path('profile/', users_views.profile, name='profile'),
]