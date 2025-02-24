# Generated by Django 5.1.5 on 2025-01-25 09:16

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, validators=[django.core.validators.EmailValidator(message='Invalid email format.')])),
                ('phone', models.CharField(blank=True, help_text='Enter digits only.', max_length=20, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Phone number must contain digits only.', regex='^\\d+$')])),
                ('role', models.CharField(choices=[('doctor', 'Doctor'), ('patient', 'Patient')], max_length=20)),
                ('gender', models.CharField(blank=True, max_length=10, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('profile_photo', models.URLField(blank=True, help_text='Store a URL or relative path.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='DoctorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_number', models.CharField(max_length=100, unique=True)),
                ('specialization', models.CharField(max_length=255)),
                ('years_experience', models.PositiveIntegerField(default=0)),
                ('clinic_name', models.CharField(blank=True, max_length=255, null=True)),
                ('clinic_address', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PatientProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insurance_details', models.CharField(blank=True, max_length=255, null=True)),
                ('medical_history', models.TextField(blank=True, null=True)),
                ('emergency_contact', models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator(message='Emergency contact must contain digits only.', regex='^\\d+$')])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='patient_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['email'], name='accounts_cu_email_5ce40b_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['phone'], name='accounts_cu_phone_c30b3c_idx'),
        ),
    ]
