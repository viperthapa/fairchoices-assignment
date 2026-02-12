import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from core.models import Country, Role

User = get_user_model()


@pytest.fixture
def user_payload(country):
    """Valid user creation payload"""
    return {
        "username": "testuser123",
        "email": "testuser@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "role": "COUNTRY_MEMBER",
        "country_id": country.id,
    }


@pytest.fixture
def invalid_user_payloads(country):
    """Various invalid user payloads for validation testing"""
    return {
        "password_mismatch": {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Pass123!",
            "confirm_password": "Pass456!",
            "role": "COUNTRY_MEMBER",
            "country_id": country.id,
        },
        "weak_password": {
            "username": "testuser",
            "email": "test@example.com",
            "password": "pass",
            "confirm_password": "pass",
            "role": "COUNTRY_MEMBER",
            "country_id": country.id,
        },
        "existing_username": {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "role": "COUNTRY_MEMBER",
            "country_id": country.id,
        },
        "existing_email": {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "role": "COUNTRY_MEMBER",
            "country_id": country.id,
        },
        "invalid_email": {
            "username": "testuser",
            "email": "invalid-email",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "role": "COUNTRY_MEMBER",
            "country_id": country.id,
        },
        "short_username": {
            "username": "ab",
            "email": "test@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "role": "COUNTRY_MEMBER",
            "country_id": country.id,
        },
        "missing_country_for_admin": {
            "username": "newadmin",
            "email": "admin@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!",
            "role": "COUNTRY_ADMIN",
        },
    }


# ============================================
# User List Tests
# ============================================
@pytest.mark.django_db
def test_list_users_as_super_admin_success(super_admin_client, multiple_users):
    """Test super admin can list all users"""
    url = reverse("user-list")
    response = super_admin_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= len(multiple_users)


@pytest.mark.django_db
def test_list_users_as_country_admin_success(country_admin_client, country):
    """Test country admin can only list users from their country"""
    # Create users in same country
    User.objects.create_user(
        username="user1",
        email="user1@test.com",
        password="TestPass123!",
        role=Role.COUNTRY_MEMBER,
        country=country,
    )
    User.objects.create_user(
        username="user2",
        email="user2@test.com",
        password="TestPass123!",
        role=Role.COUNTRY_MEMBER,
        country=country,
    )

    # Create user in different country
    other_country = Country.objects.create(
        name="Other Country", capital="Other Capital"
    )
    User.objects.create_user(
        username="otheruser",
        email="other@test.com",
        password="TestPass123!",
        role=Role.COUNTRY_MEMBER,
        country=other_country,
    )

    url = reverse("user-list")
    response = country_admin_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    # Should only see users from their country (including self)
    assert len(response.data) == 3  # country_admin + 2 users
    for user_data in response.data:
        assert user_data["country"] == country.id


@pytest.mark.django_db
def test_list_users_as_country_member_success(
    country_member_client, country_member_user, country
):
    """Test country member can only see themselves"""
    # Create other users in same country
    User.objects.create_user(
        username="other1",
        email="other1@test.com",
        password="TestPass123!",
        role=Role.COUNTRY_MEMBER,
        country=country,
    )

    url = reverse("user-list")
    response = country_member_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == country_member_user.id
    assert response.data[0]["email"] == country_member_user.email


@pytest.mark.django_db
def test_create_user_as_super_admin_success(super_admin_client, user_payload):
    """Test super admin can create user in any country"""
    url = reverse("user-list")
    response = super_admin_client.post(url, user_payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == user_payload["username"]
    assert response.data["email"] == user_payload["email"]
    assert User.objects.count() == 2  # super_admin + new user


@pytest.mark.django_db
def test_create_user_as_country_admin_same_country_success(
    country_admin_client, country
):
    """Test country admin can create user in their country"""
    payload = {
        "username": "newuser123",
        "email": "newuser@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "role": "COUNTRY_MEMBER",
        "country_id": country.id,
    }
    url = reverse("user-list")
    response = country_admin_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(email="newuser@example.com")
    assert user.country.id == country.id
    assert user.role == Role.COUNTRY_MEMBER


@pytest.mark.django_db
def test_create_user_as_country_admin_different_country_fail(country_admin_client):
    """Test country admin cannot create user in different country"""
    other_country = Country.objects.create(name="Other", capital="Other Capital")
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "role": "COUNTRY_MEMBER",
        "country_id": other_country.id,
    }
    url = reverse("user-list")
    response = country_admin_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert User.objects.count() == 1  # Only the country admin


@pytest.mark.django_db
def test_create_user_as_country_member_fail(country_member_client, country):
    """Test country member cannot create users"""
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "role": "COUNTRY_MEMBER",
        "country_id": country.id,
    }
    url = reverse("user-list")
    response = country_member_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert User.objects.count() == 1  # Only the country member


# ============================================
# CREATE USER - VALIDATION TESTS
# ============================================


@pytest.mark.django_db
def test_create_user_duplicate_username_validation(super_admin_client, country):
    """Test duplicate username validation"""
    # Create a user first
    User.objects.create_user(
        username="existinguser",
        email="existing@example.com",
        password="TestPass123!",
        role=Role.COUNTRY_MEMBER,
        country=country,
    )

    payload = {
        "username": "existinguser",  # Duplicate username
        "email": "new@example.com",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "role": "COUNTRY_MEMBER",
        "country_id": country.id,
    }
    url = reverse("user-list")
    response = super_admin_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data
    assert "already exists" in str(response.data["username"]).lower()


@pytest.mark.django_db
def test_create_user_duplicate_email_validation(super_admin_client, country):
    """Test duplicate email validation"""
    # Create a user first
    User.objects.create_user(
        username="existinguser",
        email="existing@example.com",
        password="TestPass123!",
        role=Role.COUNTRY_MEMBER,
        country=country,
    )

    payload = {
        "username": "newuser",
        "email": "existing@example.com",  # Duplicate email
        "password": "TestPass123!",
        "confirm_password": "TestPass123!",
        "role": "COUNTRY_MEMBER",
        "country_id": country.id,
    }
    url = reverse("user-list")
    response = super_admin_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
    assert "already exists" in str(response.data["email"]).lower()
