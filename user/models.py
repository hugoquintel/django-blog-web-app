from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def user_profile_picture_path(instance, filename):
    # This file will be upload to MEDIA_ROOT / username / filename
    return f"{instance.user.username}/profile_picture/{filename}"


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followings = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False, blank=True
    )
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    education = models.CharField(max_length=100, null=True, blank=True)
    work = models.CharField(max_length=100, null=True, blank=True)
    link = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(max_length=200, null=True, blank=True)
    picture = models.ImageField(
        upload_to=user_profile_picture_path, null=True, blank=True
    )

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()
        profile.followings.set([instance.profile.id])
        profile.save()


# @receiver(pre_save, sender=Profile)
# def auto_delete_file_on_change(sender, instance, **kwargs):
#     if not instance.pk:
#         return
#     try:
#         profile = Profile.objects.get(pk=instance.pk)
#     except Profile.DoesNotExist:
#         return
#     if profile.picture and instance.picture and profile.picture != instance.picture:
#         # Delete the old file if it doesn't match the newly submitted one
#         profile.picture.delete(save=False)
