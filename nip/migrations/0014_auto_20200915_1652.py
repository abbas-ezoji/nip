# Generated by Django 2.1.15 on 2020-09-15 12:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nip', '0013_shiftconstpersonneltimes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shiftconstdayrequirements',
            name='ShiftAssignment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nip.ShiftAssignments'),
        ),
        migrations.AlterField(
            model_name='shiftconstpersonneltimes',
            name='Personnel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nip.Personnel'),
        ),
        migrations.AlterField(
            model_name='shiftconstpersonneltimes',
            name='ShiftAssignment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nip.ShiftAssignments'),
        ),
    ]