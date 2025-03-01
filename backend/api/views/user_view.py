from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from api.exceptions.custom_exceptions import LoginFailed
from api.models import User
from api.serializers import (
    UserSerializer, UserUpdateSerializer, UserRegisterSerializer, UserUpdatePasswordSerializer
)
from api.permissions import IsAdmin, IsUserOwner


# User API to list users
class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'All users have been listed successfully',
            'users': serializer.data
        }, status=status.HTTP_200_OK)
    

# User API to create user
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        
        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'User created successfully',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
            

# User API to retrieve user by id
class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
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
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'User not found {str(e)}')
        
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'User retrieved successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    

# User API to update user information
class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'       

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'User not found {str(e)}')
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(f'User not updated: {serializer.errors}')
        
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'User information updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    

# User API to delete User
class UserDeleteAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if Token.objects.filter(user=instance).exists():
            token = Token.objects.get(user=instance)
            token.delete()
        return super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'User not found {str(e)}')

        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': f'User "{instance}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    
# User API to update password
class UserPasswordUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdatePasswordSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsUserOwner]
    lookup_field = 'id'

    def perform_update(self, serializer):
        instance = serializer.instance
        new_password = serializer.validated_data['new_password']
        instance.set_password(new_password)
        instance.save()

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            raise NotFound(f'User not found: {str(e)}')
        
        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():    
            raise ValidationError(f'Password not updated: {serializer.errors}')
        
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Password updated successfully',
        }, status=status.HTTP_200_OK)

    
# User API to register user
class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        self.perform_create(serializer)
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
    

# User API to login user
class UserLoginAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()

        if not user:
            raise LoginFailed('Email does not exist')
        if not user.is_active:
            raise LoginFailed('Account is not active')
        if not user.check_password(password):
            raise LoginFailed('Password is incorrect')
        
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)
        return Response({
            'success': True,
            'message': f'Login successful ({'created' if created else 'existing'} token)',
            'token': token.key,
            'user': user_serializer.data
        })            
    

# User API to logout user
class UserLogoutAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsUserOwner]

    def delete(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token.delete()
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)    