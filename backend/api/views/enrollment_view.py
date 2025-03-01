from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from api.exceptions.custom_exceptions import Existed
from api.models import Enrollment, Course
from api.serializers import (
    EnrollmentSerializer, PaymentSerializer, CourseSerializer
)
from api.permissions import IsAdmin, IsCourseOwner, IsStudent


# Enrollment API to list all enrollments
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
    

# Enrollment API to list enrollments in a course
class EnrollmentListByCourseAPIView(generics.ListAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCourseOwner | IsAdmin]
    
    def list(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise NotFound('Course not found')
        
        queryset = course.enrollments.all()
        serializer = EnrollmentSerializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'All enrollments in the course have been listed successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
# Enrollment API to list all courses a student has enrolled in
class EnrolledCoursesByStudentAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student = self.request.user
        return Course.objects.filter(enrollments__student=student, is_visible=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = CourseSerializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'All enrolled courses have been listed successfully',
            'courses': serializer.data
        }, status=status.HTTP_200_OK)

    
# Enrollment API to create a enrollment
class EnrollmentCreateAPIView(generics.CreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    def create(self, request, *args, **kwargs):

        course_id = self.kwargs.get('course_id')
        course = Course.objects.filter(id=course_id).first()
        if not course:
            raise NotFound('Course not found')
        request.data['course_id'] = course.id

        student = request.user
        if course.enrollments.filter(student=student).exists():
            raise Existed('You have already enrolled in this course')
        request.data['student_id'] = student.id

        if not course.get_discounted_price() == 0:
            # Create payment
            payment_serializer = PaymentSerializer(data={'amount': course.get_discounted_price()})
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
    

# Enrollment API to retrieve a enrollment
class EnrollmentRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Enrollment.DoesNotExist:
            raise NotFound('Enrollment not found')
        
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Enrollment retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    


# Enrollment API to update a enrollment



# Enrollment API to delete a enrollment
class EnrollmentDeleteAPIView(generics.DestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Enrollment.DoesNotExist:
            raise NotFound('Enrollment not found')
        
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Enrollment deleted successfully',
        }, status=status.HTTP_204_NO_CONTENT)
