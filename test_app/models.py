from django.db import models
from django.contrib.auth.models import AbstractUser, Permission

class User(AbstractUser):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=7, choices=ROLE_CHOICES, blank=True, null=True)
    specialization = models.CharField(max_length=20, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='test_app_user_set'
    )

    class Meta:
        app_label = 'test_app'


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(User, limit_choices_to={'role': 'teacher'}, related_name='courses_taught', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, through='Enrollment', related_name='courses_enrolled')

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(User, limit_choices_to={'role': 'student'}, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"

class Comment(models.Model):
    course = models.ForeignKey(Course, related_name='comments', on_delete=models.CASCADE)
    student = models.ForeignKey(User, limit_choices_to={'role': 'student'}, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.student.username} on {self.course.title} at {self.created_at}"
    

