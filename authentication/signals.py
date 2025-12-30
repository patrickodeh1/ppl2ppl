from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def assign_default_group(sender, instance, created, **kwargs):
    """Assign new users to a default group."""
    if created:
        try:
            default_group = Group.objects.get(name='Users')
            instance.groups.add(default_group)
        except Group.DoesNotExist:
            # Create the group if it doesn't exist
            default_group = Group.objects.create(name='Users')
            instance.groups.add(default_group)
