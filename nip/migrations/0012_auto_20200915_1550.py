# Generated by Django 2.1.15 on 2020-09-15 11:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nip', '0011_auto_20200913_1521'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShiftConstDayRequirements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Day', models.IntegerField()),
                ('PersonnelCount', models.IntegerField()),
                ('PersonnelPoints', models.IntegerField()),
                ('RequireMinCount', models.IntegerField()),
                ('RequireMaxCount', models.IntegerField()),
                ('RequireMeanCount', models.IntegerField()),
                ('DiffMinCount', models.IntegerField()),
                ('DiffMaxCount', models.IntegerField()),
                ('DiffCount', models.IntegerField()),
                ('PersonnelTypes', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='nip.PersonnelTypes')),
                ('ShiftAssignment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='nip.ShiftAssignments')),
                ('ShiftTypes', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='nip.ShiftTypes')),
            ],
            options={
                'verbose_name_plural': 'نیازمندی روزانه',
            },
        ),
        migrations.AlterField(
            model_name='tkp_logs',
            name='Personnel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='nip.Personnel'),
        ),
    ]
