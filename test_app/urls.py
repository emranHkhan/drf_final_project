from django.urls import path
from .views import (
    UserList, UserDetail,
    CategoryList, CategoryDetail,
    CourseList, CourseDetail,
    EnrollmentList, EnrollmentDetail,
    CommentList, CommentDetail, UserRegistrationView,UserLoginApiView, UserLogoutApiView, ActivateAccountView, EnrollmentListByStudent, CourseCreateAPIView, TeacherList
)

urlpatterns = [
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('courses/', CourseList.as_view(), name='course-list'), # course by teacher and course by category also implemented
    path('courses/<int:pk>/', CourseDetail.as_view(), name='course-detail'),
    path('enrollments/', EnrollmentList.as_view(), name='enrollment-list'), # need to work on this
    path('enrollments/student/<int:student_id>/', EnrollmentListByStudent.as_view(), name='enrollments-by-student'),
    path('comments/', CommentList.as_view(), name='comment-list'), # need to work on this
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginApiView.as_view(), name='login'),
    path('logout/', UserLogoutApiView.as_view(), name='logout'),
    path('active/<uid64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('courses/create/', CourseCreateAPIView.as_view(), name='course-create'),
    path('teachers/', TeacherList.as_view(), name='teacher-list'),
    # path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
    # path('teachers/<int:pk>/', TeacherDetail.as_view(), name='teacher-detail'),
    # path('students/', StudentList.as_view(), name='student-list'),
    # path('students/<int:pk>/', StudentDetail.as_view(), name='student-detail'),
    # path('enrollments/<int:pk>/', EnrollmentDetail.as_view(), name='enrollment-detail'),
    # path('comments/<int:pk>/', CommentDetail.as_view(), name='comment-detail'),
]
