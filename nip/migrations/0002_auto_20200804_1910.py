# Generated by Django 2.1.15 on 2020-08-04 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nip', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personnelshiftdateassignments',
            name='D01',
            field=models.IntegerField(default=1, verbose_name='روز 01'),
        ),
    ]
