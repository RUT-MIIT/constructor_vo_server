from django.urls import include, path
from dj_rest_auth.views import PasswordResetConfirmView

from rest_framework.routers import DefaultRouter
from ai.views import chat_with_gpt, IshDataNsisWizardView
from programs.views import ProgramViewSet, NsiViewSet, NsiTypeViewSet, MinistryViewSet, EducationLevelListView, \
    EducationDirectionListView, ProgramRoleListView, MyProgramsListView, ProgramInformationView, IshDataView, \
    ProductViewSet, SyncNsiWithProductView, ProcessViewSet, LifeStageViewSet, RecDtView, SyncNsiWithLifeStageView, \
    SyncNsiWithProcessView, MultiplicityTypesListView, CompetenceViewSet, DisciplineViewSet
from ai.views import IshDataProductsWizardView, ish_data_products_step_1, ish_data_products_step_2, ish_data_products_step_3, ish_data_products_step_4
from users.views import UserListView


router = DefaultRouter()


router.register(r'programs', ProgramViewSet)


# router.register(r'processes/(?P<process_id>\d+)/results', ProcessResultViewSet)

# router.register(r'programs/(?P<program_id>\d+)/disciplines', DisciplineViewSet)

router.register(r'programs/(?P<program_id>\d+)/nsis', NsiViewSet)
router.register(r'nsi_types', NsiTypeViewSet)
router.register(r'ministries', MinistryViewSet)

router.register(r'programs/(?P<program_id>\d+)/products', ProductViewSet)
router.register(r'products/(?P<product_id>\d+)/stages', LifeStageViewSet)
router.register(r'stages/(?P<stage_id>\d+)/processes', ProcessViewSet)
router.register(r'programs/(?P<program_id>\d+)/competences', CompetenceViewSet,  basename='competence')
router.register(r'programs/(?P<program_id>\d+)/disciplines', DisciplineViewSet,  basename='discipline')

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('rest-auth/password/reset/confirm/', PasswordResetConfirmView.as_view(),
           name='password_reset_confirm'),

    path('education_levels/', EducationLevelListView.as_view()),
    path('education_directions/', EducationDirectionListView.as_view()),
    path('program_roles/', ProgramRoleListView.as_view()),
    path('my_programs/', MyProgramsListView.as_view()),

    path('users/', UserListView.as_view()),

    # Пути для загрузки информации этапа
    path('programs/<int:pk>/information/', ProgramInformationView.as_view()),
    # openai
    path('chat/', chat_with_gpt, name='chat_with_gpt'),

    # Исходные данные этапов
    path('programs/<int:program_id>/stages/ish_data', IshDataView.as_view()), # этап 1
    path('programs/<int:program_id>/stages/rec_dt', RecDtView.as_view()), # этап 1

    # AI - исходные данные - продукты
    path('programs/<int:program_id>/stages/ish_data/wizards/ish_data_products', IshDataProductsWizardView.as_view()),
    path('programs/<int:program_id>/stages/ish_data/wizards/ish_data_products/steps/ish_data_products_step_1', ish_data_products_step_1.as_view()),
    path('programs/<int:program_id>/stages/ish_data/wizards/ish_data_products/steps/ish_data_products_step_2', ish_data_products_step_2.as_view()),
    path('programs/<int:program_id>/stages/ish_data/wizards/ish_data_products/steps/ish_data_products_step_3', ish_data_products_step_3.as_view()),
    path('programs/<int:program_id>/stages/ish_data/wizards/ish_data_products/steps/ish_data_products_step_4', ish_data_products_step_4.as_view()),
    # AI - исходные данные - пНСИ
    path('programs/<int:program_id>/stages/ish_data/wizards/ish_data_nsis', IshDataNsisWizardView.as_view()),

    path('products/<int:product_id>/sync-nsi/', SyncNsiWithProductView.as_view(), name='sync-nsi-with-product'),
    path('stages/<int:stage_id>/sync-nsi/', SyncNsiWithLifeStageView.as_view(), name='sync-nsi-with-stage'),
    path('processes/<int:process_id>/sync-nsi/', SyncNsiWithProcessView.as_view(), name='sync-nsi-with-process'),

    path('multiplicity-types/', MultiplicityTypesListView.as_view(), name='multiplicity-types-list'),

] + router.urls
