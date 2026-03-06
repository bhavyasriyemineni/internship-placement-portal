# student/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..recruiter.models import Application
from core.models import Notification # Import your new model

@receiver(post_save, sender=Application)
def trigger_status_notification(sender, instance, created, **kwargs):
    if not created: # Triggered on status updates (Round 1, Round 2, Selected)
        Notification.objects.create(
            recipient=instance.student,
            notification_type='status',
            title="Application Status Updated",
            message=f"Your application for {instance.opportunity.title} has been moved to: {instance.get_status_display()}."
        )