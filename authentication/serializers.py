from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from rest_framework.fields import SerializerMethodField


from .models import User
from django.contrib.auth.hashers import make_password


class SignupSerializer(serializers.ModelSerializer):
    """override create method to change the password into hash."""

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data.get("password"))
        return super(SignupSerializer, self).create(validated_data)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', "first_name", "last_name"]


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password']


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(source="auth_token.key", read_only=True)


    class Meta:
        model = User
        fields = [ 'id','username', 'email', 'groups', 'access_token', 'first_name','last_name', 'user_permissions']
        depth = 1
        extra_kwargs = {'password': {'write_only': True}}





class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['name']



class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=False)
    step = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=False)



