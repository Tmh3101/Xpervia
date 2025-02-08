from django.urls import path
from api.views import user_view, course_view, chapter_view, lesson_view

urlpatterns = [
    # User URLs
    path('users/', user_view.UserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<uuid:id>/', user_view.UserDetailAPIView.as_view(), name='user-detail'),
    path('users/<uuid:id>/update/', user_view.UserUpdateAPIView.as_view(), name='user-update'),
    path('users/<uuid:id>/update-password/', user_view.UserPasswordUpdateAPIView.as_view(), name='user-password-update'),

    path('register/', user_view.UserRegisterAPIView.as_view(), name='user-register'),
    path('token/login/', user_view.CustomAuthTokenAPIView.as_view(), name='token_obtain_pair'),
    path('token/logout/', user_view.UserLogoutAPIView.as_view(), name='api_token_logout'),

    # Course URLs
    path('courses/', course_view.CourseListAPIView.as_view(), name='course-list'),
    path('courses/create/', course_view.CourseCreateAPIView.as_view(), name='course-create'),
    path('courses/<int:id>/', course_view.CourseRetrievelAPIView.as_view(), name='course-detail'),
    path('courses/<int:id>/update/', course_view.CourseUpdateDeleteAPIView.as_view(), name='course-update'),
    path('courses/<int:id>/delete/', course_view.CourseUpdateDeleteAPIView.as_view(), name='course-delete'),
    path('courses/<int:id>/detail/', course_view.CourseDetailAPIView.as_view(), name='course-lesson-list'),

    # Chapter URLs
    path('courses/<int:course_id>/chapters/', chapter_view.ChapterListAPIView.as_view(), name='chapter-list'),
    path('courses/<int:course_id>/chapters/create/', chapter_view.ChapterCreateAPIView.as_view(), name='chapter-create'),
    path('courses/chapters/<int:id>/', chapter_view.ChapterRetrieveAPIView.as_view(), name='chapter-detail'),
    path('courses/chapters/<int:id>/update/', chapter_view.ChapterUpdateDeleteAPIView.as_view(), name='chapter-update'),
    path('courses/chapters/<int:id>/delete/', chapter_view.ChapterUpdateDeleteAPIView.as_view(), name='chapter-delete'),
    path('courses/chapters/<int:id>/detail/', chapter_view.ChapterDetailAPIView.as_view(), name='chapter-lessons-list'),

    # Lesson URLs
    path('courses/<int:course_id>/lessons/', lesson_view.LessonListByCourseAPIView.as_view(), name='lesson-list'),
    path('courses/<int:course_id>/chapters/<int:chapter_id>/lessons/', lesson_view.LessonListByChapterAPIView.as_view(), name='lesson-list'),
    path('courses/<int:course_id>/lessons/create/', lesson_view.LessonCreateAPIView.as_view(), name='lesson-create'),
    path('courses/lessons/<int:id>/', lesson_view.LessonRetrieveAPIView.as_view(), name='lesson-detail'),
    path('courses/lessons/<int:id>/update/', lesson_view.LessonUpdateDeleteAPIView.as_view(), name='lesson-update'),
    path('courses/lessons/<int:id>/delete/', lesson_view.LessonUpdateDeleteAPIView.as_view(), name='lesson-delete'),
]