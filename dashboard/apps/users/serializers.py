from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import transaction
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'bio')

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'bio')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        try:
            # Remove password2 as it's not needed anymore
            validated_data.pop('password2', None)
            # Sanitize bio field
            bio = validated_data.pop('bio', '').strip()
            
            user = User.objects.create(
                username=validated_data['username'],
                email=validated_data['email'],
                bio=bio
            )
            user.set_password(validated_data['password'])
            user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError(str(e))

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Consider if username is really needed in the token
        return token