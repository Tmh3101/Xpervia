from rest_framework import serializers
from api.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_of_birth', 'role', 'password', 'is_active', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True},
        }

    def create(self, validated_data):
        password = validated_data.get('password')
        if password and len(password) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long')
        user = User.objects.create_user(**validated_data)
        return user


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']  
    

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_of_birth', 'role', 'is_active']
        extra_kwargs = {
            'email': {'required': False}
        }

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
    
        
class UserUpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if not self.context['request'].user.check_password(data.get('old_password')):
            raise serializers.ValidationError({'old_password': 'Wrong password'})
        if data.get('old_password') == data.get('new_password'):
            raise serializers.ValidationError({'new_password': 'New password must be different from old password'})
        return data  
    

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_of_birth', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user