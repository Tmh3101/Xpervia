from django.urls import path
from api.views import (
    user_view,
    category_view,
    chapter_view,
    lesson_view,
    assignment_view,
    enrollment_view,
    submission_view,
    submission_score_view,
    lesson_completion_view,
    course_view
)

urlpatterns = [
    # User URLs
    path('users/', user_view.UserListAPIView.as_view(), name='user-list'),
    path('users/create/', user_view.UserCreateAPIView.as_view(), name='user-create'),
    path('users/<uuid:id>/', user_view.UserRetrieveAPIView.as_view(), name='user-detail'),
    path('users/<uuid:id>/update/', user_view.UserUpdateAPIView.as_view(), name='user-update'),
    path('users/<uuid:id>/delete/', user_view.UserDeleteAPIView.as_view(), name='user-delete'),
    path('users/<uuid:id>/update-password/', user_view.UserPasswordUpdateAPIView.as_view(), name='user-password-update'),
    path('register/', user_view.UserRegisterAPIView.as_view(), name='user-register'),
    path('token/login/', user_view.UserLoginAPIView.as_view(), name='token-login'),
    path('token/logout/', user_view.UserLogoutAPIView.as_view(), name='token-logout'),

    # Course Category URLs
    path('courses/categories/', category_view.CategoryListAPIView.as_view(), name='category-list'),
    path('courses/categories/create/', category_view.CategoryCreateAPIView.as_view(), name='category-create'),
    path('courses/categories/<int:id>/', category_view.CategoryRetrieveAPIView.as_view(), name='category-detail'),
    path('courses/categories/<int:id>/update/', category_view.CategoryUpdateAPIView.as_view(), name='category-update'),
    path('courses/categories/<int:id>/delete/', category_view.CategoryDeleteAPIView.as_view(), name='category-delete'),

    # Course URLs
    path('courses/', course_view.CourseListAPIView.as_view(), name='course-list'),
    path('courses/teacher/', course_view.CourseListByTeacherAPIView.as_view(), name='course-list-teacher'),
    path('courses/create/', course_view.CourseCreateAPIView.as_view(), name='course-create'),
    path('courses/<int:id>/', course_view.CourseRetrieveAPIView.as_view(), name='course-detail'),
    path('courses/<int:id>/update/', course_view.CourseUpdateAPIView.as_view(), name='course-update'),
    path('courses/<int:id>/delete/', course_view.CourseDeleteAPIView.as_view(), name='course-delete'),
    path('courses/<int:id>/detail-lessons/', course_view.CourseRetrieveWithDetailLessonsAPIView.as_view(), name='course-detail-lessons'),

    # Enrollment URLs
    path('courses/enrollments/', enrollment_view.EnrollmentListAPIView.as_view(), name='enrollment-list'),
    path('courses/<int:course_id>/enrollments/', enrollment_view.EnrollmentListByCourseAPIView.as_view(), name='enrollment-list'),
    path('courses/<int:course_id>/enrollments/create/', enrollment_view.EnrollmentCreateAPIView.as_view(), name='course-enroll'),
    path('courses/enrollments/<int:id>/', enrollment_view.EnrollmentRetrieveAPIView.as_view(), name='enrollment-detail'),
    # path('courses/enrollments/<int:id>/update/', enrollment_view.EnrollmentUpdateAPIView.as_view(), name='enrollment-update'),
    path('courses/enrollments/<int:id>/delete/', enrollment_view.EnrollmentDeleteAPIView.as_view(), name='enrollment-delete'),
    path('courses/enrollments/student/', enrollment_view.EnrollmentListByStudentAPIView.as_view(), name='enrollment-student-list'),

    # Chapter URLs
    path('courses/<int:course_id>/chapters/', chapter_view.ChapterListAPIView.as_view(), name='chapter-list'),
    path('courses/<int:course_id>/chapters/create/', chapter_view.ChapterCreateAPIView.as_view(), name='chapter-create'),
    path('courses/chapters/<int:id>/', chapter_view.ChapterRetrieveAPIView.as_view(), name='chapter-detail'),
    path('courses/chapters/<int:id>/update/', chapter_view.ChapterUpdateAPIView.as_view(), name='chapter-update'),
    path('courses/chapters/<int:id>/delete/', chapter_view.ChapterDeleteAPIView.as_view(), name='chapter-delete'),

    # Lesson URLs
    path('courses/<int:course_id>/lessons/', lesson_view.LessonListByCourseAPIView.as_view(), name='lesson-list'),
    path('courses/chapters/<int:chapter_id>/lessons/', lesson_view.LessonListByChapterAPIView.as_view(), name='lesson-list'),
    path('courses/<int:course_id>/lessons/create/', lesson_view.LessonCreateAPIView.as_view(), name='lesson-create'),
    path('courses/lessons/<int:id>/', lesson_view.LessonRetrieveAPIView.as_view(), name='lesson-detail'),
    path('courses/lessons/<int:id>/update/', lesson_view.LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('courses/lessons/<int:id>/delete/', lesson_view.LessonDeleteAPIView.as_view(), name='lesson-delete'),

    # Lesson Completion URLs
    path('courses/lessons/<int:lesson_id>/completions/', lesson_completion_view.LessonCompletionListAPIView.as_view(), name='lesson-complete-list'),
    path('courses/<int:course_id>/lessons/completions/student/', lesson_completion_view.LessonCompletionListByStudentAPIView.as_view(), name='lesson-complete-list'),
    path('courses/lessons/<int:lesson_id>/completions/create/', lesson_completion_view.LessonCompletionCreateAPIView.as_view(), name='lesson-complete'),
    path('courses/lessons/<int:lesson_id>/completions/delete/', lesson_completion_view.LessonCompletionDeleteAPIView.as_view(), name='lesson-complete-delete'),

    # Assignment URLs
    path('courses/lessons/<int:lesson_id>/assignments/', assignment_view.AssignmentListAPIView.as_view(), name='assignment-list'),
    path('courses/lessons/<int:lesson_id>/assignments/create/', assignment_view.AssignmentCreateAPIView.as_view(), name='assignment-create'),
    path('courses/lessons/assignments/<int:id>/', assignment_view.AssignmentRetrieveAPIView.as_view(), name='assignment-detail'),
    path('courses/lessons/assignments/<int:id>/update/', assignment_view.AssignmentUpdateAPIView.as_view(), name='assignment-update'),
    path('courses/lessons/assignments/<int:id>/delete/', assignment_view.AssignmentDeleteAPIView.as_view(), name='assignment-delete'),

    # Submission URLs
    path('courses/assignments/<int:assignment_id>/submissions/', submission_view.SubmissionListByAssignmentAPIView.as_view(), name='submission-list'),
    path('courses/assignments/<int:assignment_id>/submissions/create/', submission_view.SubmissionCreateAPIView.as_view(), name='submission-create'),
    path('courses/assignments/submissions/<int:id>/', submission_view.SubmissionRetrieveAPIView.as_view(), name='submission-detail'),
    path('courses/assignments/submissions/<int:id>/update/', submission_view.SubmissionUpdateAPIView.as_view(), name='submission-update'),
    path('courses/assignments/submissions/<int:id>/delete/', submission_view.SubmissionDeleteAPIView.as_view(), name='submission-delete'),

    # Submission Score URLs
    path('courses/assignments/submissions/<int:submission_id>/score/', submission_score_view.SubmissionScoreCreateAPIView.as_view(), name='submission-score-create'),
    path('courses/assignments/submissions/score/<int:id>/update/', submission_score_view.SubmissionScoreUpdateAPIView.as_view(), name='submission-score-update'),
    path('courses/assignments/submissions/score/<int:id>/delete/', submission_score_view.SubmissionScoreDeleteAPIView.as_view(), name='submission-score-delete'),
]