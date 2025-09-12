import logging
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from api.models import  User
from api.serializers import UserSerializer
from api.permissions import IsAdmin, IsUserOwner
from api.middlewares.authentication import SupabaseJWTAuthentication
from api.services.supabase.client import supabase
from api.services.supabase import auth

logger = logging.getLogger(__name__)


# Users API to list all users
class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request, *args, **kwargs):
        logger.info("Listing all users")
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        logger.info("Successfully listed users")
        return Response({
            'success': True,
            'message': 'All users have been listed successfully',
            'users': serializer.data
        }, status=status.HTTP_200_OK)


# User API to create a user
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        role = request.data.get("role")

        logger.info("Creating a new user in supabase auth")
        response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "first_name": first_name,
                "last_name": last_name,
                "role": role
            },
        })

        user_id = response.user.id

        logger.info("Creating a new user in database")
        user_serializer = self.get_serializer(data={
            "id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": role
        })
        
        if not user_serializer.is_valid():
            supabase.auth.admin.delete_user(user_id)
            raise ValidationError(f'User not created: {user_serializer.errors}')
        
        self.perform_create(user_serializer)
        headers = self.get_success_headers(user_serializer.data)
        logger.info("User created successfully")
        return Response({
            'success': True,
            'message': 'User created successfully',
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    

# Chapter API to retrieve a chapter
class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving user with ID: {kwargs.get('id')}")
        try:    
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'User not found: {str(e)}')
    
        serializer = self.get_serializer(instance)
        user_data = serializer.data.copy()
        logger.info("User retrieved successfully")
        return Response({
            'success': True,
            'message': 'User retrieved successfully',
            'user': user_data
        }, status=status.HTTP_200_OK)
    

# User API to update a user
class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsUserOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating user with ID: {kwargs.get('id')}")
        try:    
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'User not found: {str(e)}')

        logger.info("Updating user in database")
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(f'User not updated: {serializer.errors}')
        
        try:
            logger.info("Updating user metadata in supabase auth")
            update_data = {
                "email": request.data.get("email"),
                "password": request.data.get("password"),
                "user_metadata": {
                    "first_name": request.data.get("first_name"),
                    "last_name": request.data.get("last_name"),
                    "role": request.data.get("role")
                }
            }
            # Remove None values from update_data
            update_data = {k: v for k, v in update_data.items() if v is not None}
            supabase.auth.admin.update_user_by_id(instance.id, update_data)
        except Exception as e:
            logger.error(f"Error updating user metadata in supabase auth: {str(e)}")
            raise ValidationError(f'User not updated in supabase: {str(e)}')

        self.perform_update(serializer)
        logger.info("User updated successfully")
        return Response({
            'success': True,
            'message': 'User updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    

# User API to delete a user
class UserDeleteAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting user with ID: {kwargs.get('id')}")
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'User not found: {str(e)}')

        try:
            logger.info("Deleting user metadata in supabase auth")
            supabase.auth.admin.delete_user(instance.id)
        except Exception as e:
            logger.error(f"Error deleting user metadata in supabase auth: {str(e)}")
            raise ValidationError(f'User not deleted in supabase: {str(e)}')

        self.perform_destroy(instance)
        logger.info("User deleted successfully")
        return Response({
            'success': True,
            'message': f'User "{instance}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    
    
class UserDisableAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Disabling user with ID: {kwargs.get('id')}")
        try:    
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'User not found: {str(e)}')

        serializer = self.get_serializer(instance, data={"is_active": False}, partial=True)
        if not serializer.is_valid():
            raise ValidationError(f'User not disabled: {serializer.errors}')

        self.perform_update(serializer)

        logger.info("User disabled successfully")
        return Response({
            'success': True,
            'message': 'User disabled successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)


class UserEnableAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Enabling user with ID: {kwargs.get('id')}")
        try:    
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'User not found: {str(e)}')

        serializer = self.get_serializer(instance, data={"is_active": True}, partial=True)
        if not serializer.is_valid():
            raise ValidationError(f'User not enabled: {serializer.errors}')

        self.perform_update(serializer)

        logger.info("User enabled successfully")
        return Response({
            'success': True,
            'message': 'User enabled successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    

class UserChangePasswordAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SupabaseJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsUserOwner]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Changing password for user with ID: {kwargs.get('id')}")
        try:    
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'User not found: {str(e)}')

        new_password = request.data.get("new_password")
        if not new_password:
            raise ValidationError('New password is required')
        
        try:
            auth.login(instance.email, request.data.get("old_password"))
        except Exception as e:
            logger.error(f"Error signing in user: {str(e)}")
            raise ValidationError(e)

        try:
            logger.info("Changing user password in supabase auth")
            supabase.auth.admin.update_user_by_id(instance.id, {
                "password": new_password
            })
        except Exception as e:
            logger.error(f"Error changing user password in supabase auth: {str(e)}")
            raise ValidationError(f'Password not changed in supabase: {str(e)}')

        logger.info("Password changed successfully")
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)