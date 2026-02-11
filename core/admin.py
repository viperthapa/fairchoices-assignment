from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

from core.models import AuditLog, Country, Project, User

# Register your models here.
admin.site.register(Country)
admin.site.register(AuditLog)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "country", "status", "created_by", "created_at")
    list_filter = ("status", "country")  # Only fields that exist in Project
    search_fields = ("title", "description", "created_by__email")


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ("username", "email", "role", "country", "is_staff", "is_active")
    list_filter = ("role", "country", "is_staff", "is_active")

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("role", "country")}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("role", "country")}),
    )