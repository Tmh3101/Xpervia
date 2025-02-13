from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from api.serializers.user_serializer import UserSerializer, UserUpdateSerializer, UserRegisterSerializer, UserUpdatePasswordSerializer
from api.roles.admin_role import IsAdmin
from api.roles.user_checking import IsUserOwner

User = get_user_model()

# User API to list and create users for Admin
class UserListCreateAPIView(generics.ListCreateAPIView):
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
            'data': serializer.data
        }, status=status.HTTP_200_OK)    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'User not created',
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'User created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
            

# User API to retrieve, update, and delete user by id for Admin
class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin | IsUserOwner]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response({
                'success': False,
                'message': 'User not found',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'User retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except Http404 as e:
            return Response({
                'success': False,
                'message': 'User not found',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'User deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    

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
            return Response({
                'success': False,
                'message': 'User not found',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'User information not updated',
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'User information updated successfully',
            'data': serializer.data
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
            return Response({
                'success': False,
                'message': 'User not found',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'User deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    
# User API to update password for User
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
            return Response({
                'success': False,
                'message': 'User not found',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():    
            return Response({
                'success': False,
                'message': 'Password not updated',
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Password updated successfully'
        }, status=status.HTTP_200_OK)

    
# User API to register user for User
class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'User not registered',
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    

# Custom Auth Token API to login user
class CustomAuthTokenAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({
                'success': False,
                'message': 'Invalid email'
            }, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({
                'success': False,
                'message': 'User is not active'
            }, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({
                'success': False,
                'message': 'Invalid password'
            }, status=status.HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'success': True,
            'message': 'Login successful',
            'token': token.key
        })        
    
    
class UserLogoutAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsUserOwner]

    def delete(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)