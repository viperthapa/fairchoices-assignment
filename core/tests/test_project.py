import pytest
from rest_framework import status
from django.urls import reverse
from core.models import Project, ProjectStatus, AuditLog
from datetime import date, timedelta
from decimal import Decimal



@pytest.fixture
def project(country, super_admin_user):
    """Create a single project"""
    project = Project.objects.create(
        title="Test Project",
        description="Test Description",
        status=ProjectStatus.ACTIVE,
        created_by=super_admin_user,
        country=country,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        budget=Decimal("10000.00"),
        is_deleted=False
    )
    return project

@pytest.fixture
def another_project(another_country, super_admin_user):
    """Create another project for testing"""
    project = Project.objects.create(
        title="Another Project",
        description="Another Description",
        status=ProjectStatus.ACTIVE,
        created_by=super_admin_user,
        country=another_country,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=60),
        budget=Decimal("20000.00"),
        is_deleted=False
    )
    return project

@pytest.fixture
def deleted_project(country, super_admin_user):
    """Create a soft-deleted project"""
    project = Project.objects.create(
        title="Deleted Project",
        description="This project is deleted",
        status=ProjectStatus.ARCHIVED,
        created_by=super_admin_user,
        country=country,
        is_deleted=True
    )
    return project

@pytest.fixture
def multiple_projects(country, super_admin_user):
    """Create multiple projects for list testing"""
    projects = []
    for i in range(5):
        project = Project.objects.create(
            title=f"Project {i}",
            description=f"Description {i}",
            status=ProjectStatus.ACTIVE if i % 2 == 0 else ProjectStatus.INACTIVE,
            created_by=super_admin_user,
            country=country,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30 * (i + 1)),
            budget=Decimal(f"{10000 * (i + 1)}.00"),
            is_deleted=False
        )
        projects.append(project)
    return projects

@pytest.fixture
def project_payload(country):
    """Valid project creation payload"""
    return {
        "title": "New Test Project",
        "description": "New Test Description",
        "status": "ACTIVE",
        "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=30)).isoformat(),
        "budget": "15000.00",
        "country_id": country.id
    }

@pytest.fixture
def invalid_project_payloads():
    """Various invalid project payloads for validation testing"""
    return {
        "empty_title": {"title": "", "description": "Test"},
        "missing_title": {"description": "Test"},
        "future_start_date": {
            "title": "Test", "description": "Test",
            "start_date": (date.today() + timedelta(days=1)).isoformat()
        },
        "end_date_before_start": {
            "title": "Test", "description": "Test",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() - timedelta(days=1)).isoformat()
        },
        "negative_budget": {
            "title": "Test", "description": "Test",
            "budget": "-1000.00"
        },
        "invalid_status": {
            "title": "Test", "description": "Test",
            "status": "INVALID_STATUS"
        }
    }

@pytest.fixture
def audit_log(super_admin_user, project):
    """Create an audit log entry"""
    audit_log = AuditLog.objects.create(
        user=super_admin_user,
        user_email=super_admin_user.email,
        model_name="Project",
        object_id=project.id,
        object_repr=str(project),
        action="create",
        changes={"title": "Test Project"}
    )
    return audit_log



@pytest.mark.django_db
def test_create_project_as_super_admin_success(super_admin_client, project_payload):
    """Test super admin can create project successfully"""
    url = reverse('project-list')
    response = super_admin_client.post(url, project_payload, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['title'] == project_payload['title']
    assert response.data['description'] == project_payload['description']
    assert response.data['status'] == project_payload['status']
    assert Decimal(response.data['budget']) == Decimal(project_payload['budget'])
    
    # Verify database
    assert Project.objects.count() == 1
    project = Project.objects.first()
   
    # Verify audit log was created
    assert AuditLog.objects.filter(
        model_name="Project",
        action="create",
        object_id=project.id
    ).exists()
@pytest.mark.django_db
def test_create_project_as_country_admin_success(country_admin_client, country, project_payload):
    """Test country admin can create project in their country"""
    project_payload['country_id'] = country.id
    url = reverse('project-list')
    response = country_admin_client.post(url, project_payload, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    project = Project.objects.first()
    assert project.country.id == country.id
    assert project.created_by == country_admin_client.handler._force_user



# ============================================
# UPDATE PROJECT TESTS
# ============================================
@pytest.mark.django_db
def test_update_project_as_super_admin_success(super_admin_client, project):
    """Test super admin can fully update any project"""
    url = reverse('project-detail', args=[project.id])
    updated_data = {
        'title': 'Updated Title',
        'description': 'Updated Description',
        'status': ProjectStatus.INACTIVE,
        'budget': '25000.00'
    }
    response = super_admin_client.put(url, updated_data, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    project.refresh_from_db()
    assert project.title == 'Updated Title'
    assert project.description == 'Updated Description'
    assert project.status == ProjectStatus.INACTIVE
    assert project.budget == Decimal('25000.00')
    
    # Verify audit log was created
    assert AuditLog.objects.filter(
        model_name="Project",
        action="update",
        object_id=project.id
    ).exists()



@pytest.mark.django_db
def test_delete_project_as_super_admin_success(super_admin_client, project):
    """Test super admin can hard delete any project"""
    url = reverse('project-detail', args=[project.id])
    response = super_admin_client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Project.objects.filter(id=project.id).exists()
    
    assert AuditLog.objects.filter(
        model_name="Project",
        action="delete",
        object_id=project.id
    ).exists()

@pytest.mark.django_db
def test_delete_project_as_country_admin_same_country_success(country_admin_client, project):
    """Test country admin can delete project in their country"""
    project.country = country_admin_client.handler._force_user.country
    project.save()
    
    url = reverse('project-detail', args=[project.id])
    response = country_admin_client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Project.objects.filter(id=project.id).exists()

