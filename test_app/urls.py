from django.urls import path
from .views import (
    UserList, UserDetail,
    CategoryList,
    CourseList, CourseDetail,
    EnrollmentList,
    CommentList, UserRegistrationView, UserLoginApiView, UserLogoutApiView, ActivateAccountView, EnrollmentListByStudent, CourseCreateAPIView, TeacherList, list_urls
)

urlpatterns = [
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('courses/', CourseList.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetail.as_view(), name='course-detail'),
    path('enrollments/', EnrollmentList.as_view(), name='enrollment-list'), 
    path('enrollments/student/<int:student_id>/', EnrollmentListByStudent.as_view(), name='enrollments-by-student'),
    path('comments/', CommentList.as_view(), name='comment-list'), 
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginApiView.as_view(), name='login'),
    path('logout/', UserLogoutApiView.as_view(), name='logout'),
    path('active/<uid64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('courses/create/', CourseCreateAPIView.as_view(), name='course-create'),
    path('teachers/', TeacherList.as_view(), name='teacher-list'),
    path('', list_urls, name='list_urls'),
]
