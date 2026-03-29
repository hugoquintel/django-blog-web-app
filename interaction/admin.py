from django.contrib import admin

# Register your models here.
from interaction.models import Comment, Like

# Register your models here.
admin.site.register(Comment)
admin.site.register(Like)
