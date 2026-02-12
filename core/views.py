import logging

logger = logging.getLogger(__name__)


from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog, Project
from .serializers import ProjectSerializer,UserSerializer
from .permissions import IsSuperAdmin, IsCountryAdmin, IsSuperAdminOrCountryAdmin
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import CountrySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.

class LoginView(APIView):
    permission_classes = []  # Allow anyone to login

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.filter(is_deleted=False)

    def _create_audit_log(self, instance, action):
        AuditLog.objects.create(
            user=self.request.user,
            user_email=self.request.user.email,
            model_name="Project",
            object_id=instance.id,
            object_repr=str(instance),
            action=action,
            changes=self.request.data
        )
    

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)
        self._create_audit_log(project, "create")

    def perform_update(self, serializer):
        instance = serializer.save()
        self._create_audit_log(instance, "update")

    def perform_destroy(self, instance):
        self._create_audit_log(instance, "delete")
        
        # instance.is_deleted = True #perform soft delete
        instance.delete() # Perform hard delete
        logger.info(f"Hard deleted instance with ID: {instance.id}")
   

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()


    def get_queryset(self):
        user = self.request.user

        if user.is_super_admin:
            return User.objects.all()

        if user.is_country_admin:
            return User.objects.filter(country=user.country)

        return User.objects.filter(id=user.id)

    def perform_create(self, serializer):
        creator = self.request.user
        target_country = serializer.validated_data.get("country")

        if not creator.can_create_user(target_country):
            raise PermissionDenied(
                detail="You do not have permission to create this user.",
                code=status.HTTP_403_FORBIDDEN
            ) 
             
        serializer.save()


class CountryCreateAPIView(APIView):
    """Simplified version for basic country creation"""
    permission_classes = [IsAuthenticated, IsSuperAdminOrCountryAdmin]
    
    def post(self, request):
        serializer = CountrySerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        