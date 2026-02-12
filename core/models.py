from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class Role(models.TextChoices):
    SUPER_ADMIN = "SUPER_ADMIN"
    COUNTRY_ADMIN = "COUNTRY_ADMIN"
    COUNTRY_MEMBER = "COUNTRY_MEMBER"


class ProjectStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    ARCHIVED = "ARCHIVED", "Archived"


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Country(TimeStamp):
    name = models.CharField(max_length=100, unique=True)
    capital = models.CharField(max_length=100)

    class Meta:
        db_table = "countries"
        verbose_name_plural = "Countries"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="users", null=True, blank=True
    )
    groups = models.ManyToManyField(
        Group,
        related_name="core_users",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="core_users_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username

    @property
    def is_super_admin(self):
        return self.role and self.role == Role.SUPER_ADMIN

    @property
    def is_country_admin(self):
        return self.role and self.role == Role.COUNTRY_ADMIN

    @property
    def is_country_member(self):
        return self.role and self.role == Role.COUNTRY_MEMBER

    def can_create_user(self, target_country=None):
        """Check if user can create another user for a given country"""
        if self.is_super_admin:
            return True
        if self.is_country_admin and target_country:
            return self.country == target_country
        return False

    def can_manage_user(self, target_user):
        """Check if user can manage (update/delete) another user"""
        if self.is_super_admin:
            return True
        if self.is_country_admin:
            return (
                target_user.country == self.country and not target_user.is_super_admin
            )
        return False


class Project(TimeStamp):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.ACTIVE
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_projects",
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
        blank=True,
    )
    # Optional fields for project details
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "projects"
        ordering = ["-created_at"]
        permissions = [
            ("view_all_projects", "Can view all projects"),
            ("view_country_projects", "Can view country projects"),
        ]

    def __str__(self):
        return self.title


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]

    # Who performed the action
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    user_email = (
        models.EmailField()
    )  # Store email for reference even if user is deleted

    # What was changed
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    object_repr = models.CharField(max_length=200)

    # Action details
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Change details
    changes = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return (
            f"{self.user_email} - {self.action} - {self.model_name} - {self.timestamp}"
        )
