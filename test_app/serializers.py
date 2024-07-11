from rest_framework import serializers
from .models import Enrollment, User, Course, Category, Comment

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    course_count = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'role', 'image', 'specialization', 'course_count', 'is_active']
        extra_kwargs = {
            'course_count': {'read_only': True},
        }

    def get_course_count(self, obj):
        if obj.role == 'teacher':
            return obj.courses_taught.count()
        return None

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        print(validated_data)
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            specialization=validated_data['specialization'],
            image=validated_data['image']
        )
        
        user.set_password(validated_data['password'])
        user.is_active = False 
        user.save()
        return user

# class CategorySerializer(serializers.ModelSerializer):
#     course_count = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'description', 'course_count']


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'course_count']

    def get_course_count(self, obj):
        return obj.course_set.count()
    

class CommentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='student'))
    student_name = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'student', 'student_name', 'course', 'content', 'created_at']

    def validate(self, attrs):
        student = attrs['student']
        course = attrs['course']

        # Check if the student is enrolled in the course
        if not Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("You must be enrolled in the course to comment.")

        # Check if the student has already commented on the course
        if Comment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError("You have already commented on this course.")

        return attrs
    
    def create(self, validated_data):
        return Comment.objects.create(**validated_data)



class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='teacher'), write_only=True)
    teacher_name = serializers.SerializerMethodField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.SerializerMethodField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    students = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'teacher_name', 'category', 'category_name', 'price', 'created_at', 'comments', 'students']

    def get_teacher_name(self, obj):
        return obj.teacher.username if obj.teacher else None
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
    
    def validate_teacher(self, value):
        request = self.context.get('request')
        user = request.user
        if value != user:
            raise serializers.ValidationError("You can only assign yourself as the teacher for this course.")
        return value

    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)

    
class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='student'))
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    student_info = serializers.SerializerMethodField(read_only=True)
    course_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at', 'student_info', 'course_info']

    def get_student_info(self, obj):
        student = obj.student
        return {
            "first_name": student.first_name,
            "last_name": student.last_name,
            "email": student.email,
        }

    def get_course_info(self, obj):
        course = obj.course
        return {
            "name": course.title,
            "teacher_name": course.teacher.username if course.teacher else None,
            "category": course.category.name,
            "price": course.price,
        }
    
    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        if user.role != 'student':
            raise serializers.ValidationError("Only students can enroll in courses.")
        if attrs['student'] != user:
            raise serializers.ValidationError("You can only enroll yourself in a course.")
        if Enrollment.objects.filter(student=user, course=attrs['course']).exists():
            raise serializers.ValidationError("You are already enrolled in this course.")
        return attrs

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)



