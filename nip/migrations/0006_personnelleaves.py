# Generated by Django 2.1.15 on 2020-08-30 14:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nip', '0005_auto_20200804_1923'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonnelLeaves',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PersonnelBaseId', models.IntegerField(blank=True, null=True, verbose_name='PersonnelBaseId in Chargoon')),
                ('YearWorkingPeriod', models.IntegerField()),
                ('Day', models.IntegerField()),
                ('Value', models.IntegerField()),
                ('Personnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nip.Personnel')),
                ('WorkSection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nip.WorkSection')),
            ],
            options={
                'verbose_name_plural': 'مرخصی تایید شده',
            },
        ),
    ]
