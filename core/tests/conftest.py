import os
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.cache import cache
from core.models import Country, Project, Role, ProjectStatus, AuditLog
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.hashers import make_password

User = get_user_model()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workflow.settings')

@pytest.fixture(autouse=True)
def clear_db():
    """Clear database before each test"""
    Project.objects.all().delete()
    User.objects.all().delete()
    Country.objects.all().delete()
    AuditLog.objects.all().delete()
    cache.clear()

@pytest.fixture
def api_client():
    """Return unauthenticated API client"""
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, regular_user):
    """Return authenticated API client with regular user"""
    api_client.force_authenticate(user=regular_user)
    return api_client

@pytest.fixture
def country():
    """Create a single country"""
    country = Country.objects.create(
        name="United States",
        capital="Washington, D.C."
    )
    return country

@pytest.fixture
def another_country():
    """Create another country for testing"""
    country = Country.objects.create(
        name="Canada",
        capital="Ottawa"
    )
    return country


@pytest.fixture
def multiple_users(country, another_country):
    """Create multiple users with different roles and countries using bulk_create"""
    
    hashed_password = make_password("TestPass123!")
    
    users = User.objects.bulk_create([
        # Super admin user
        User( 
            username="admin1",
            email="admin1@example.com",
            password=hashed_password,
            role=Role.SUPER_ADMIN,
            is_superuser=True,
            is_staff=True
        ), 

        # Country Admin
        User(
            username="cadm1",
            email="cadm1@example.com",
            password=hashed_password,
            role=Role.COUNTRY_ADMIN,
            country=country
        ),
        User(
            username="cadm2",
            email="cadm2@example.com",
            password=hashed_password,
            role=Role.COUNTRY_ADMIN,
            country=another_country
        ),
        # Country Members
        User(
            username="member1",
            email="member1@example.com",
            password=hashed_password,
            role=Role.COUNTRY_MEMBER,
            country=country
        ),
        User(
            username="member2",
            email="member2@example.com",
            password=hashed_password,
            role=Role.COUNTRY_MEMBER,
            country=country
        ),
        User(
            username="member3",
            email="member3@example.com",
            password=hashed_password,
            role=Role.COUNTRY_MEMBER,
            country=another_country
        ),
    ])
    
    return users

@pytest.fixture
def super_admin_client(api_client, super_admin_user):
    """Return super admin authenticated client"""
    api_client.force_authenticate(user=super_admin_user)
    return api_client



@pytest.fixture
def country_member_client(api_client, country_member_user):
    """Return country member authenticated client"""
    api_client.force_authenticate(user=country_member_user)
    return api_client

@pytest.fixture
def super_admin_user():
    """Create super admin user"""
    user = User.objects.create_user(
        username="superadmin",
        email="superadmin@example.com",
        password="TestPass123!",
        role=Role.SUPER_ADMIN,
        is_superuser=True,
        is_staff=True
    )
    return user

@pytest.fixture
def country_admin_user(country):
    """Create country admin user"""
    user = User.objects.create_user(
        username="countryadmin",
        email="countryadmin@example.com",
        password="TestPass123!",
        role=Role.COUNTRY_ADMIN,
        country=country
    )
    return user

@pytest.fixture
def country_member_user(country):
    """Create country member user"""
    user = User.objects.create_user(
        username="countrymember",
        email="countrymember@example.com",
        password="TestPass123!",
        role=Role.COUNTRY_MEMBER,
        country=country
    )
    return user
@pytest.fixture
def country_admin_client(api_client, country_admin_user):
    """Return country admin authenticated client"""
    api_client.force_authenticate(user=country_admin_user)
    return api_client

@pytest.fixture
def regular_user(country):
    """Create regular user (alias for country_member)"""
    user = User.objects.create_user(
        username="regularuser",
        email="regularuser@example.com",
        password="TestPass123!",
        role=Role.COUNTRY_MEMBER,
        country=country
    )
    return user




