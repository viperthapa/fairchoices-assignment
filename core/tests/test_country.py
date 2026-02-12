import pytest
from django.urls import reverse
from rest_framework import status

from core.models import Country


@pytest.fixture
def country_payload():
    """Valid country creation payload"""
    return {"name": "Test Country", "capital": "Test Capital"}


@pytest.mark.django_db
def test_create_country_as_super_admin_success(super_admin_client, country_payload):
    """Test super admin can create country successfully"""
    url = reverse("country-create")
    response = super_admin_client.post(url, country_payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == country_payload["name"]
    assert response.data["capital"] == country_payload["capital"]
    assert Country.objects.count() == 1


@pytest.mark.django_db
def test_create_country_unauthenticated_fail(api_client, country_payload):
    """Test unauthenticated user cannot create country"""
    url = reverse("country-create")
    response = api_client.post(url, country_payload, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Country.objects.count() == 0


@pytest.mark.django_db
def test_create_country_duplicate_name_validation(super_admin_client, country):
    """Test duplicate country name validation"""
    payload = {
        "name": country.name,  # Same name as existing country
        "capital": "New Capital",
    }
    url = reverse("country-create")
    response = super_admin_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "A country with this name already exists." in str(response.data["name"][0])


@pytest.mark.django_db
def test_create_country_duplicate_name_case_insensitive(super_admin_client, country):
    """Test case-insensitive duplicate name validation"""
    payload = {
        "name": country.name.lower(),  # Same name, different case
        "capital": "New Capital",
    }
    url = reverse("country-create")
    response = super_admin_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response = super_admin_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "A country with this name already exists." in str(response.data["name"][0])


@pytest.mark.django_db
def test_create_country_with_extra_fields(super_admin_client):
    """Test that extra fields are ignored"""
    payload = {
        "name": "Spain",
        "capital": "Madrid",
        "extra_field": "should be ignored",
        "population": "47 million",
    }
    url = reverse("country-create")
    response = super_admin_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert "extra_field" not in response.data
    assert "population" not in response.data
    country = Country.objects.first()
    assert not hasattr(country, "extra_field")
