from rest_framework import serializers
from .models import User, Project, Country


from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.validators import UniqueValidator

from .models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "country": user.country.name if user.country else None,
            }
        }



class CountrySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True
    )
    capital = serializers.CharField(required=True)

    class Meta:
        model = Country
        fields = ['id', 'name', 'capital']
        read_only_fields = ['id']


    def validate_name(self, name):
        queryset = Country.objects.filter(name__iexact=name)
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                f"A country with this name already exists."
            )
        
        return name


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with this username already exists."
            )
        ]
    )
    
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with this email address already exists."
            )
        ]
    )

    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        source="country",
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "confirm_password",
            "role",
            "country",
            "country_id"
        ]

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)
        if password != confirm_password:
            raise serializers.ValidationError({
                'error': "Passwords do not match."
            })
        
        return data
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        country_id = validated_data.pop("country_id", None)
        if country_id:
            validated_data["country"] = Country.objects.filter(id=country_id).first()
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProjectSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        source="country",
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at"]
    
    def create(self, validated_data):
        country_id = validated_data.pop("country_id", None)
        if country_id:
            validated_data["country"] = Country.objects.filter(id=country_id).first()
        return Project.objects.create(**validated_data)

    def update(self, instance, validated_data):
        country_id = validated_data.pop("country_id", None)
        if country_id:
            instance.country = Country.objects.filter(id=country_id).first()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance