from rest_framework import routers
from django.urls import path, include
from core.views import LoginView, ProjectViewSet, UserViewSet
from core.views import CountryCreateAPIView

router = routers.DefaultRouter()

router.register("users", UserViewSet,basename="user")
router.register("projects", ProjectViewSet)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path('v1/countries/', CountryCreateAPIView.as_view(), name='country-create'),
    path("v1/", include(router.urls)), 
]