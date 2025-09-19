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
    course_view,
    auth_view,
    favorite_view,
    reco_view
)

urlpatterns = [
    #=== Authentication URLs ===#
    path('auth/register/', auth_view.register_view, name='register'),
    path('auth/login/', auth_view.login_view, name='login'),
    path('auth/refresh-session/', auth_view.refresh_session_view, name='refresh-session'),
    path('auth/request-reset-password/', auth_view.request_reset_password_view, name='request-reset-password'),
    path('auth/reset-password/', auth_view.reset_password_view, name='reset-password'),
    path('auth/current-user/', auth_view.get_current_user, name='current-user'),

    path('users/<uuid:id>/change-password/', user_view.UserChangePasswordAPIView.as_view(), name='change-password'),

    #=== Admin URLs ===#
    # Users Management URLs (Admin only)
    path('admin/users/', user_view.UserListAPIView.as_view(), name='admin-user-list'),
    path('admin/users/<uuid:id>/', user_view.UserRetrieveAPIView.as_view(), name='admin-user-detail'),
    path('admin/users/create/', user_view.UserCreateAPIView.as_view(), name='admin-user-create'),
    path('admin/users/<uuid:id>/update/', user_view.UserUpdateAPIView.as_view(), name='admin-user-update'),
    path('admin/users/<uuid:id>/delete/', user_view.UserDeleteAPIView.as_view(), name='admin-user-delete'),
    path('admin/users/<uuid:id>/disable/', user_view.UserDisableAPIView.as_view(), name='admin-user-disable'),
    path('admin/users/<uuid:id>/enable/', user_view.UserEnableAPIView.as_view(), name='admin-user-enable'),

    # Category Management URLs (Admin only)
    path('admin/categories/', category_view.CategoryAdminAPIView.as_view(), name='admin-category-list-create'),
    path('admin/categories/<int:id>/', category_view.CategoryAdminAPIView.as_view(), name='admin-category-update-delete'),

    #=== Courses Management URLs ===#
    # Category URLs
    path('categories/', category_view.CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<int:id>/', category_view.CategoryDetailAPIView.as_view(), name='category-detail'),

    # Course URLs
    path('courses/', course_view.CourseListAPIView.as_view(), name='course-list'),
    path('courses/teacher/', course_view.CourseListByTeacherAPIView.as_view(), name='course-list-teacher'),
    path('courses/student/enrolled/', course_view.EnrolledCourseListAPIView.as_view(), name='enrolled-course-list'),
    path('courses/student/favorited/', course_view.FavoritedCourseListAPIView.as_view(), name='favorited-course-list'),
    path('courses/create/', course_view.CourseCreateAPIView.as_view(), name='course-create'),
    path('courses/<int:id>/', course_view.CourseRetrieveAPIView.as_view(), name='course-detail'),
    path('courses/<int:id>/update/', course_view.CourseUpdateAPIView.as_view(), name='course-update'),
    path('courses/<int:id>/delete/', course_view.CourseDeleteAPIView.as_view(), name='course-delete'),
    path('courses/<int:id>/detail-lessons/', course_view.CourseRetrieveWithDetailLessonsAPIView.as_view(), name='course-detail-lessons'),
    path('courses/<int:id>/hide/', course_view.CourseHideAPIView.as_view(), name='course-hide'),
    path('courses/<int:id>/show/', course_view.CourseShowAPIView.as_view(), name='course-show'),

    # Enrollment URLs
    path('courses/enrollments/', enrollment_view.EnrollmentListAPIView.as_view(), name='enrollment-list'),
    path('courses/<int:course_id>/enrollments/', enrollment_view.EnrollmentListByCourseAPIView.as_view(), name='enrollment-list-by-course'),
    path('courses/<int:course_id>/enroll/', enrollment_view.EnrollmentCreateAPIView.as_view(), name='course-enroll'),
    path('courses/enrollments/<int:id>/', enrollment_view.EnrollmentRetrieveAPIView.as_view(), name='enrollment-detail'),
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
    path('courses/lessons/<uuid:id>/', lesson_view.LessonRetrieveAPIView.as_view(), name='lesson-detail'),
    path('courses/lessons/<uuid:id>/update/', lesson_view.LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('courses/lessons/<uuid:id>/delete/', lesson_view.LessonDeleteAPIView.as_view(), name='lesson-delete'),

    # Lesson Completion URLs
    path('courses/lessons/<uuid:lesson_id>/completions/', lesson_completion_view.LessonCompletionListAPIView.as_view(), name='lesson-complete-list'),
    path('courses/<int:course_id>/lessons/completions/student/', lesson_completion_view.LessonCompletionListByStudentAPIView.as_view(), name='lesson-complete-list'),
    path('courses/lessons/<uuid:lesson_id>/completions/create/', lesson_completion_view.LessonCompletionCreateAPIView.as_view(), name='lesson-complete'),
    path('courses/lessons/<uuid:lesson_id>/completions/delete/', lesson_completion_view.LessonCompletionDeleteAPIView.as_view(), name='lesson-complete-delete'),

    # Assignment URLs
    path('courses/lessons/<uuid:lesson_id>/assignments/', assignment_view.AssignmentListAPIView.as_view(), name='assignment-list'),
    path('courses/lessons/<uuid:lesson_id>/assignments/student/', assignment_view.AssignmentListByStudentAPIView.as_view(), name='assignment-list-student'),
    path('courses/lessons/<uuid:lesson_id>/assignments/create/', assignment_view.AssignmentCreateAPIView.as_view(), name='assignment-create'),
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
    path('courses/assignments/submissions/<int:submission_id>/score/create/', submission_score_view.SubmissionScoreCreateAPIView.as_view(), name='submission-score-create'),
    path('courses/assignments/submissions/score/<int:id>/update/', submission_score_view.SubmissionScoreUpdateAPIView.as_view(), name='submission-score-update'),
    path('courses/assignments/submissions/score/<int:id>/delete/', submission_score_view.SubmissionScoreDeleteAPIView.as_view(), name='submission-score-delete'),

    # Favorite URLs
    path('favorites/', favorite_view.FavoriteListAPIView.as_view(), name='favorite-list'),
    path('favorites/course/<int:course_id>/', favorite_view.FavoriteListByCourseAPIView.as_view(), name='favorite-list-by-course'),
    path('favorites/student/', favorite_view.FavoriteListByStudentAPIView.as_view(), name='favorite-list-by-student'),
    path('favorites/create/<int:course_id>/', favorite_view.FavoriteCreateAPIView.as_view(), name='favorite-create'),
    path('favorites/<int:id>/', favorite_view.FavoriteRetrieveAPIView.as_view(), name='favorite-detail'),
    path('favorites/<int:course_id>/delete/', favorite_view.FavoriteDeleteAPIView.as_view(), name='favorite-delete'),

    #=== Recommendation URLs ===#
    path('reco/courses/similar/<int:course_id>/', reco_view.SimilarCourseListAPIView.as_view(), name='similar-course-list'),
    path('reco/courses/home/', reco_view.HomeRecoListAPIView.as_view(), name='recommend-home'),
]