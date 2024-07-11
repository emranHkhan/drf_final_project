from django.contrib import admin

from .models import User, Category, Course, Enrollment, Comment

admin.site.register([User, Category, Course, Enrollment, Comment])