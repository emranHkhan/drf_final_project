from django.utils.html import format_html
from django.http import HttpResponse
from django.urls import get_resolver, reverse
from rest_framework import generics, permissions, status
from .models import User, Category, Course, Enrollment, Comment
from .serializers import UserSerializer, CategorySerializer, CourseSerializer, EnrollmentSerializer, CommentSerializer, UserLoginSerializer
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CourseList(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    ordering_fields = ['title', 'created_at']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        total_count = queryset.count()

        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            'total_count': total_count,
            'courses': serializer.data
        }

        return Response(response_data)

    def get_queryset(self):
        queryset = Course.objects.all()

        teacher_id = self.request.query_params.get('teacher')

        if teacher_id:
            # if not self.request.user.role == 'teacher':
            #     queryset = queryset.none()  
            #     return queryset

            # queryset = queryset.filter(teacher_id=teacher_id, teacher=self.request.user)
            queryset = queryset.filter(teacher_id=teacher_id)

        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        ordering = self.request.query_params.get('ordering')
        if ordering in self.ordering_fields:
            queryset = queryset.order_by(ordering)

        return queryset

class CourseCreateAPIView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            "request": self.request
        })
        return context

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'teacher':
            raise PermissionDenied("Only teachers can create courses.")
        serializer.save()

class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Course.objects.filter(teacher=user)
        raise PermissionDenied("Please Login to see all courses.")

    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_authenticated or user.role != 'teacher':
            raise PermissionDenied("You do not have permission to edit this course.")
        if serializer.instance.teacher != user:
            raise PermissionDenied("You do not have permission to edit this course.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_authenticated or user.role != 'teacher':
            raise PermissionDenied("You do not have permission to delete this course.")
        if instance.teacher != user:
            raise PermissionDenied("You do not have permission to delete this course.")
        instance.delete()
class EnrollmentList(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            "request": self.request
        })
        return context

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'student':
            raise PermissionDenied("Only students can enroll in courses.")
        serializer.save()

class EnrollmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            "request": self.request
        })
        return context
    
    def perform_create(self, serializer):
        serializer.save()

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class EnrollmentListByStudent(generics.ListAPIView):
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        return Enrollment.objects.filter(student_id=student_id)

class UserRegistrationView(APIView):
    serializer_class = UserSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save() 
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f"http://127.0.0.1:8000/api/active/{uid}/{token}"
            email_subject = "Confirm Your Email"
            email_body = render_to_string('confirm_email.html', {'confirm_link': confirm_link})
            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()
            return Response({"message":"Check your email for confirmation.", "credentials": {"uid": uid, "token": token}})
        return Response(serializer.errors)

class ActivateAccountView(APIView):
    def get(self, request, uid64, token):
        try:
            uid = urlsafe_base64_decode(uid64).decode()
            user = User._default_manager.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'failure'}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginApiView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)
                return Response({'token': token.key, 'user_id': user.id, 'user_email' : user.email, 'user_role' : user.role, 'image_url' : user.image, 'user_name': user.username})
            return Response({'error': 'Invalid username or password'})
        return Response(serializer.errors)
    
class UserLogoutApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError):
            pass
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

class TeacherList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(role='teacher')

# test_app/views.py
from django.conf import settings
from django.http import HttpResponse
from django.urls import get_resolver, reverse
from django.utils.html import format_html

# Dictionary to map URL names to descriptions
url_descriptions = {
    'user-list': 'List all users',
    'user-detail': 'Detail view of a specific user',
    'category-list': 'List all categories',
    'course-list': 'List all courses (by teacher and category)',
    'course-detail': 'Detail view of a specific course',
    'enrollment-list': 'List all enrollments',
    'enrollments-by-student': 'List all enrollments for a specific student',
    'comment-list': 'List all comments',
    'register': 'User registration',
    'login': 'User login',
    'logout': 'User logout',
    'activate': 'Activate user account',
    'course-create': 'Create a new course',
    'teacher-list': 'List all teachers',
}

# Determine the base URL based on the environment
if settings.DEBUG:
    base_url = 'http://127.0.0.1:8000/api/'
else:
    base_url = 'https://online-school-drf.onrender.com/api/'

def list_urls(request):
    urlconf = get_resolver()
    urls = urlconf.reverse_dict.keys()
    response = '<h1>Available URLs</h1><ul>'
    for url in urls:
        if isinstance(url, str):  # Filter out non-string keys
            try:
                url_path = reverse(url)
                full_url = base_url + url_path.lstrip('/')
                description = url_descriptions.get(url, 'No description available')
                response += format_html('<li><a href="{}">{}</a> - {}</li>', full_url, url, description)
            except Exception as e:
                # Handle exceptions for URL patterns that require parameters
                response += format_html('<li>{} (URL requires parameters) - {}</li>', url, description)
    response += '</ul>'
    return HttpResponse(response)
