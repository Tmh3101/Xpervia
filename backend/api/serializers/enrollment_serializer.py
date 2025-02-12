from api.models.enrollment_model import Enrollment
from api.models.payment_model import Payment
from api.models.user_model import User
from api.models.course_detail_model import CourseDetail
from api.serializers.payment_serializer import PaymentSerializer
from api.serializers.user_serializer import SimpleUserSerializer
from api.serializers.course_detail_serializer import CourseDetailSerializer
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
            'id': {'read_only': True},
            'created_at': {'read_only': True}
        }