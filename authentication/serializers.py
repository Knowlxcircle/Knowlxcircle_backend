from rest_framework import serializers
from .models import Member, SocialMedia

# myapp/serializers.py

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class RegisterMemberSerializer(serializers.Serializer):
    """Validates the register-member body the frontend sends."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    occupation = serializers.CharField(
        max_length=50, required=False, allow_blank=True, allow_null=True, default=''
    )
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')

    def validate_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('This field may not be blank.')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

class MemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Member
        fields = ('id', 'user', 'username', 'occupation', 'bio')
        read_only_fields = ('id', 'user')

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username

        return token


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = "__all__"
