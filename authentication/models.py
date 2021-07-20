from django.db import models
from django.contrib.auth.models import User
from basic_information import models as bs

levels = (
    (1, ("دانشگاه")),
    (2, ("بیمارستان")),
    (3, ("بخش ")),
)


class UserProfile(models.Model):
    User = models.OneToOneField(User, models.CASCADE)
    Hospital = models.ForeignKey(bs.Hospital, models.DO_NOTHING, null=True, blank=True)
    WorkSection = models.ForeignKey(bs.WorkSection, models.DO_NOTHING, null=True, blank=True)
    Level = models.IntegerField(choices=levels, default=1)
