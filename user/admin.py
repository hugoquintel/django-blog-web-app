from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# Register your models here.
class CustomUserAdmin(UserAdmin):
    # Add custom fields to the fieldsets for the change form
    list_display = ("id",) + UserAdmin.list_display
    fieldsets = UserAdmin.fieldsets + (
        (
            "Profile",
            {
                "classes": ("collapse",),
                "fields": (
                    "is_private",
                    "birthday",
                    "address",
                    "education",
                    "work",
                    "link",
                    "bio",
                    "picture",
                    "followings",
                ),
            },
        ),
    )
    # Add custom fields to the fieldsets for the add form
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Profile",
            {
                "classes": ("collapse",),
                "fields": (
                    "is_private",
                    "birthday",
                    "address",
                    "education",
                    "work",
                    "link",
                    "bio",
                    "picture",
                    "followings",
                ),
            },
        ),
    )
    ordering = ("id",)


admin.site.register(User, CustomUserAdmin)
