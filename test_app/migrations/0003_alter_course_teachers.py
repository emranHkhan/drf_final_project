# Generated by Django 5.0.6 on 2024-07-07 18:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0002_remove_course_teachers_course_teachers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='teachers',
            field=models.OneToOneField(blank=True, limit_choices_to={'role': 'teacher'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courses_taught', to=settings.AUTH_USER_MODEL),
        ),
    ]
