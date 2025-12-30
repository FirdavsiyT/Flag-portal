from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Solve, Attempt

@receiver(post_save, sender=Solve)
def broadcast_solve(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'global_updates',
            {
                'type': 'event_update',
                'event_type': 'data_refresh', # Универсальное событие для обновления данных
                'message': f'User {instance.user.username} solved {instance.challenge.title}!'
            }
        )

@receiver(post_save, sender=Attempt)
def broadcast_attempt(sender, instance, created, **kwargs):
    if created:
        # Обновляем дашборд (Activity Log) при любой попытке
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'global_updates',
            {
                'type': 'event_update',
                'event_type': 'data_refresh',
                'message': 'New activity'
            }
        )