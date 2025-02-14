from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from api.exceptions.custom_exceptions import Existed
from api.models.enrollment_model import Enrollment
from api.models.course_detail_model import CourseDetail
from api.serializers.enrollment_serializer import EnrollmentSerializer
from api.serializers.payment_serializer import PaymentSerializer
from api.permissions.admin_permissions_checker import IsAdmin

# Enrollment API to list
class EnrollmentListAPIView(generics.ListAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = EnrollmentSerializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'All enrollments have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
# Enrollment API to create
class CourseEnrollAPIView(generics.CreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        course_detail_id = self.kwargs.get('course_id')
        course_detail = CourseDetail.objects.filter(id=course_detail_id).first()
        if not course_detail:
            raise NotFound('Course not found')
        request.data['course_detail_id'] = course_detail.id

        student = request.user
        if course_detail.enrollments.filter(student=student).exists():
            raise Existed('You have already enrolled in this course')
        request.data['student_id'] = student.id

        if not course_detail.get_discounted_price() == 0:
            # Create payment
            payment_serializer = PaymentSerializer(data={'amount': course_detail.get_discounted_price()})
            if not payment_serializer.is_valid():
                raise ValidationError(f'Payment not created: {payment_serializer.errors}')
            payment = payment_serializer.save()
            request.data['payment_id'] = payment.id

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(f'Enrollment not created: {serializer.errors}')
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Enrollment created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


