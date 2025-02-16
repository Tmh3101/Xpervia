from api.models import Enrollment, CourseDetail, Payment, User
from .payment_serializer import PaymentSerializer
from .user_serializer import SimpleUserSerializer
from .course_detail_serializer import CourseDetailSerializer
from rest_framework import serializers


class EnrollmentSerializer(serializers.ModelSerializer):
    student = SimpleUserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='student',
        write_only=True
    )

    course_detail = CourseDetailSerializer(read_only=True)
    course_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseDetail.objects.all(),
        source='course_detail',
        write_only=True
    )

    payment = PaymentSerializer(read_only=True)
    payment_id = serializers.PrimaryKeyRelatedField(
        queryset=Payment.objects.all(),
        source='payment',
        write_only=True
    )

    
    class Meta:
        model = Enrollment
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True}
        }