# Generated by Django 5.1.5 on 2025-01-25 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_specialization_remove_doctorprofile_specialization_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='fullname',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
