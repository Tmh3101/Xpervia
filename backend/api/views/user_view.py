import logging
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.exceptions.custom_exceptions import LoginFailed
from api.models import User
from api.serializers import (
    UserSerializer,
    UserUpdateSerializer,
    UserRegisterSerializer,
    UserUpdatePasswordSerializer
)
from api.permissions import IsAdmin, IsUserOwner

logger = logging.getLogger(__name__)

# User API to list users
class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request, *args, **kwargs):
        logger.info("Listing all users")
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        logger.info("Successfully listed all users")
        return Response({
            'success': True,
            'message': 'All users have been listed successfully',
            'users': serializer.data
        }, status=status.HTTP_200_OK)
    

# User API to create user
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        logger.info("Creating a new user")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"User creation failed: {serializer.errors}")
            raise ValidationError(serializer.errors)
        
        self.perform_create(serializer)
        logger.info("User created successfully")
        return Response({
            'success': True,
            'message': 'User created successfully',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
    
# User API to get my information
class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        logger.info(f"User information retrieved: {serializer.data}")
        return Response({
            'success': True,
            'user': serializer.data
        })
            

# User API to retrieve user by id
class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsUserOwner]
    lookup_field = 'id'

    def check_permissions(self, request):
        results = []
        for permission in self.get_permissions():
            if not isinstance(permission, IsAuthenticated):
                try:
                    permission.has_permission(request, self)
                    results.append(True)
                except PermissionDenied:
                    results.append(False)
        if not any(results):
            raise PermissionDenied('You are not allowed to perform this action')

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving user with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            logger.error(f"User not found: {str(e)}")
            raise NotFound(f'User not found {str(e)}')
        
        serializer = self.get_serializer(instance)
        logger.info("User retrieved successfully")
        return Response({
            'success': True,
            'message': 'User retrieved successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    

# User API to update user information
class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsUserOwner]
    lookup_field = 'id'       

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating user with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            logger.error(f"User not found: {str(e)}")
            raise NotFound(f'User not found {str(e)}')
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            logger.error(f"User update failed: {serializer.errors}")
            raise ValidationError(f'User not updated: {serializer.errors}')
        
        self.perform_update(serializer)
        logger.info("User information updated successfully")
        return Response({
            'success': True,
            'message': 'User information updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    

# User API to delete User
class UserDeleteAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if Token.objects.filter(user=instance).exists():
            token = Token.objects.get(user=instance)
            token.delete()
        return super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting user with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            logger.error(f"User not found: {str(e)}")
            raise NotFound(f'User not found {str(e)}')

        self.perform_destroy(instance)
        logger.info(f"User '{instance}' deleted successfully")
        return Response({
            'success': True,
            'message': f'User "{instance}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    
# User API to update password
class UserPasswordUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdatePasswordSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsUserOwner]
    lookup_field = 'id'

    def perform_update(self, serializer):
        instance = serializer.instance
        new_password = serializer.validated_data['new_password']
        instance.set_password(new_password)
        instance.save()

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating password for user with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            logger.error(f"User not found: {str(e)}")
            raise NotFound(f'User not found: {str(e)}')
        
        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():    
            logger.error(f"Password update failed: {serializer.errors}")
            raise ValidationError(f'Password not updated: {serializer.errors}')
        
        self.perform_update(serializer)
        logger.info("Password updated successfully")
        return Response({
            'success': True,
            'message': 'Password updated successfully',
        }, status=status.HTTP_200_OK)

    
# User API to register user
class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    authentication_classes = []  # No authentication required for registration
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("Registering a new user")
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"User registration failed: {serializer.errors}")
            raise ValidationError(serializer.errors)

        self.perform_create(serializer)
        logger.info("User registered successfully")
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
    

# User API to disable user account
class UserDisableAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Disabling user account with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            logger.error(f"User not found: {str(e)}")
            raise NotFound(f'User not found: {str(e)}')
        
        instance.is_active = False
        instance.save()
        logger.info("User account disabled successfully")
        return Response({
            'success': True,
            'message': 'User account disabled successfully',
            'user': UserSerializer(instance).data
        }, status=status.HTTP_200_OK)
    
# User API to enable user account
class UserEnableAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Enabling user account with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            logger.error(f"User not found: {str(e)}")
            raise NotFound(f'User not found: {str(e)}')
        
        instance.is_active = True
        instance.save()
        logger.info("User account enabled successfully")
        return Response({
            'success': True,
            'message': 'User account enabled successfully',
            'user': UserSerializer(instance).data
        }, status=status.HTTP_200_OK)