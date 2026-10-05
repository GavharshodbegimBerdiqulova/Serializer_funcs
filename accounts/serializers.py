from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Parollar bir xil emas'})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)

    def to_representation(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return {'username': user.username, 'email': user.email, 'token': token.key}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError("Username yoki parol noto'g'ri")
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        token, _ = Token.objects.get_or_create(user=validated_data['user'])
        return token

    def to_representation(self, token):
        return {'token': token.key}


class LogoutSerializer(serializers.Serializer):
    def save(self, **kwargs):
        user = self.context['request'].user
        Token.objects.filter(user=user).delete()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError("Eski parol noto'g'ri")
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context['request'].user)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        Token.objects.filter(user=user).delete()
        return Token.objects.create(user=user)
