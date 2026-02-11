from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Project, AuditLog

@receiver(post_save, sender=Project)
def project_saved(sender, instance, created, **kwargs):
    AuditLog.objects.create(
        user=getattr(instance, "_user", None),
        action="CREATE" if created else "UPDATE",
        model_name="Project",
        object_id=instance.id,
        changes={"title": instance.title, "status": instance.status}
    )


@receiver(post_delete, sender=Project)
def project_deleted(sender, instance, **kwargs):
    AuditLog.objects.create(
        user=getattr(instance, "_user", None),
        action="DELETE",
        model_name="Project",
        object_id=instance.id,
    )
