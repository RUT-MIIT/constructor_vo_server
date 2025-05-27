
from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from llm import views as llm_views

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="Описание API для моего приложения",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls'), name='api'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('login/', llm_views.login_view, name='login'),
    path('home/', llm_views.home_view, name='home'),
    path('chains/', llm_views.chains_view, name='chain_list'),
    path('chain/<int:pk>/', llm_views.chain_detail, name='chain_detail'),
    path('chain/<int:pk>/edit/', llm_views.chain_edit, name='chain_edit'),
    path('chain/<int:pk>/clone/', llm_views.chain_clone, name='chain_clone'),

    path('chain/<int:pk>/delete/', llm_views.chain_delete, name='chain_delete'),
    path('chain/new/', llm_views.chain_create, name='chain_create'),

    path('results/', llm_views.results_list, name='results_list'),
    path('results/<int:run_id>/', llm_views.result_detail, name='result_detail'),

    path('load-params/', llm_views.load_chain_inputs, name='load_chain_inputs'),
    path('generate-result/', llm_views.generate_result, name='generate_result'),

    path('load_run_result/', llm_views.load_run_result, name='load_run_result'),


]
