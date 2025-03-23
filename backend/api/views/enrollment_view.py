from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound, ValidationError
from api.exceptions.custom_exceptions import Existed
from api.models import Enrollment, Course, LessonCompletion, CourseContent
from api.serializers import (
    EnrollmentSerializer, PaymentSerializer, SimpleEnrollmentSerializer, CourseContentSerializer
)
from api.permissions import IsAdmin, IsCourseOwner, IsStudent

def get_course_progress(course_content, student):
    total_lessons = course_content.lessons.count()
    completed_lessons = LessonCompletion.objects.filter(
        lesson__course_content=course_content, student=student
    ).count()
    return round(completed_lessons / total_lessons * 100, 2) if total_lessons > 0 else 0


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
            'enrollments': serializer.data
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
        enrollments = EnrollmentSerializer(queryset, many=True).data.copy()

        for enrollment in enrollments:
            student = enrollment['student']
            student_id = student['id']
            enrollment['progress'] = get_course_progress(course.course_content, student_id)

        return Response({
            'success': True,
            'message': 'All enrollments in the course have been listed successfully',
            'enrollments': enrollments
        }, status=status.HTTP_200_OK)
    
# Enrollment API to list all courses a student has enrolled in
class EnrollmentListByStudentAPIView(generics.ListAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(student=request.user)
        enrollments = EnrollmentSerializer(queryset, many=True).data.copy()

        for enrollment in enrollments:
            course = enrollment['course']
            course_conent_id = course['course_content']['id']
            course_content = CourseContent.objects.filter(id=course_conent_id).first()
            enrollment['progress'] = get_course_progress(course_content, request.user)

        return Response({
            'success': True,
            'message': 'All enrolled courses have been listed successfully',
            'enrollments': enrollments
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
