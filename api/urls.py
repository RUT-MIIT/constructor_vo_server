from django.urls import include, path
from dj_rest_auth.views import PasswordResetConfirmView

from rest_framework.routers import DefaultRouter

from programs.views import ProgramViewSet, NsiViewSet, NsiTypeViewSet, MinistryViewSet, EducationLevelListView, \
    EducationDirectionListView, ProgramRoleListView, MyProgramsListView, ProgramInformationView

router = DefaultRouter()


router.register(r'programs', ProgramViewSet)
# router.register(r'programs/(?P<program_id>\d+)/products', ProductViewSet)
# router.register(r'products/(?P<product_id>\d+)/stages', LifeStageViewSet)
# router.register(r'stages/(?P<stage_id>\d+)/processes', ProcessViewSet)
# router.register(r'processes/(?P<process_id>\d+)/results', ProcessResultViewSet)

# router.register(r'programs/(?P<program_id>\d+)/disciplines', DisciplineViewSet)

router.register(r'programs/(?P<program_id>\d+)/nsis', NsiViewSet)
router.register(r'nsi_types', NsiTypeViewSet)
router.register(r'ministries', MinistryViewSet)

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('rest-auth/password/reset/confirm/', PasswordResetConfirmView.as_view(),
           name='password_reset_confirm'),

    path('education_levels/', EducationLevelListView.as_view()),
    path('education_directions/', EducationDirectionListView.as_view()),
    path('program_roles/', ProgramRoleListView.as_view()),
    path('my_programs/', MyProgramsListView.as_view()),

    # Пути для загрузки информации этапа
    path('programs/<int:pk>/information/', ProgramInformationView.as_view()),
] + router.urls



