from django.urls import path
from .views import user_view, course_view

urlpatterns = [
    path('users/', user_view.UserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<uuid:id>/', user_view.UserDetailAPIView.as_view(), name='user-detail'),
    path('users/<uuid:id>/update/', user_view.UserUpdateAPIView.as_view(), name='user-update'),
    path('users/<uuid:id>/update-password/', user_view.UserPasswordUpdateAPIView.as_view(), name='user-password-update'),

    path('register/', user_view.UserRegisterAPIView.as_view(), name='user-register'),
    path('token/login/', user_view.CustomAuthTokenAPIView.as_view(), name='token_obtain_pair'),
    path('token/logout/', user_view.UserLogoutAPIView.as_view(), name='api_token_logout'),

    path('courses/', course_view.CourseListAPIView.as_view(), name='course-list'),
    path('courses/create/', course_view.CourseCreateAPIView.as_view(), name='course-create'),
    path('courses/<int:id>/', course_view.CourseRetrievelAPIView.as_view(), name='course-detail'),
    path('courses/<int:id>/update/', course_view.CourseUpdateDeleteAPIView.as_view(), name='course-update'),
    path('courses/<int:id>/delete/', course_view.CourseUpdateDeleteAPIView.as_view(), name='course-delete'),
]