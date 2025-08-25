from api.models import Enrollment, Course, Payment
from .payment_serializer import PaymentSerializer
from .course_serializer import CourseSerializer, SimpleCourseSerializer
from rest_framework import serializers
from api.models import User


class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()

    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )

    payment = PaymentSerializer(read_only=True)
    payment_id = serializers.PrimaryKeyRelatedField(
        queryset=Payment.objects.all(),
        source='payment',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Enrollment
        fields = '__all__'
        extra_kwargs = {
            'student_id': {'write_only': True},
            'created_at': {'read_only': True},
            'payment': {'required': False}
        }

    def get_student(self, obj):
        if obj.student_id:
            return User.objects.get(id=obj.student_id).to_dict()
        return None


class SimpleEnrollmentSerializer(serializers.ModelSerializer):
    course = SimpleCourseSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'payment', 'created_at']