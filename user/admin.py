from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User, Follow


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
                ),
            },
        ),
    )
    ordering = ("id",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow)
