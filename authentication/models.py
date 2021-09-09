from django.db import models
from django.contrib.auth.models import User
from basic_information import models as bs

levels = (
    (1, ("دانشگاه")),
    (2, ("بیمارستان")),
    (3, ("بخش ")),
    (4, ("پرستار")),
)


class UserProfile(models.Model):
    User = models.OneToOneField(User, models.CASCADE)
    Hospital = models.ForeignKey(bs.Hospital, models.DO_NOTHING, null=True, blank=True)
    WorkSection = models.ForeignKey(bs.WorkSection, models.DO_NOTHING, null=True, blank=True)
    Level = models.IntegerField(choices=levels, default=1)
    PersonnelNo = models.CharField('شماره پرسنلی شخصی', max_length=20, null=True, blank=True)

    def __str__(self):
        return self.User.username

    def Personnel(self):
        personnel = bs.Personnel.objects.filter(User=self.User)
        print('personnel = ', personnel)
        return personnel

    def save(self, *args, **kwargs):
        if not self.id or self.PersonnelNo is None:
            super().save(*args, **kwargs)

        perno = self.PersonnelNo
        personnels = bs.Personnel.objects.filter(PersonnelNo=perno)
        for p in personnels:
            p.User = self.User
            p.save()

        super(UserProfile, self).save(*args, **kwargs)