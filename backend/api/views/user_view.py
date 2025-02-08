from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from api.serializers.user_serializer import UserSerializer, UserRegisterSerializer
from api.roles import IsAdmin

User = get_user_model()

# User API to list and create users for Admin
class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = UserSerializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'All users have been listed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'No users found'
        }, status=status.HTTP_404_NOT_FOUND)    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({
                'success': True,
                'message': 'User created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED, headers=headers)
        
        return Response({
            'success': False,
            'message': 'User not created',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
            

# User API to retrieve, update, and delete user by id for Admin
class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs.get(lookup_url_kwarg)

        if lookup_value is None:
            raise Http404("User not found, lookup_value=None")

        try:
            obj = queryset.get(**{self.lookup_field: lookup_value})
        except (User.DoesNotExist, ValidationError, ValueError):
            raise Http404("User not found")

        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'success': True,
                'message': 'User retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Http404 as e:
            return Response({
                'success': False,
                'message': 'User not found',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'User deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    

class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'id'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs.get(lookup_url_kwarg)

        if lookup_value is None:
            raise Http404("User not found, lookup_value=None")

        try:
            obj = queryset.get(**{self.lookup_field: lookup_value})
        except (User.DoesNotExist, ValidationError, ValueError):
            raise Http404("User not found")

        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'success': True,
                'message': 'User information updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'User information not updated',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class UserPasswordUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    class PasswordSerializer(serializers.Serializer):
        old_password = serializers.CharField(write_only=True)
        new_password = serializers.CharField(write_only=True)

    def get_serializer(self, *args, **kwargs):
        return self.PasswordSerializer(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            if not instance.check_password(old_password):
                return Response({
                    'success': False,
                    'message': 'Old password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            instance.set_password(new_password)
            instance.save()
            return Response({
                'success': True,
                'message': 'Password updated successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Password not updated',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    
# User API to register user for User
class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'User not registered',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

# Custom Auth Token API to login user
class CustomAuthTokenAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password) and user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'success': True,
                'message': 'Login successful',
                'token': token.key
            })
        return Response({'error': 'Invalid Credentials'}, status=400)
    
    
class UserLogoutAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

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