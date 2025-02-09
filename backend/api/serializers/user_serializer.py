from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

# User Serializer for Admin to list, create, update, and delete users
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_of_birth', 'role', 'password', 'is_active', 'date_joined']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True},
            'date_joined': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.role = validated_data.get('role', instance.role)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance
    

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
    
    
# User Register Serializer for User to register
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_of_birth', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user