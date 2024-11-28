from django.contrib import admin
from .models import Direction, EducationLevel, ProgramRole, Program, ProgramUser, NsiType, Ministry, Nsi, StageType, \
    Stage, WizardType, StepType, Wizard, Step, Product


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level', 'created_at', 'updated_at')
    search_fields = ('code', 'name')
    list_filter = ('level',)

@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(ProgramRole)
class ProgramRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('profile', 'author', 'level_id', 'direction_id', 'form', 'max_semesters', 'created_at', 'updated_at')
    search_fields = ('profile', 'author__email')
    list_filter = ('form', 'level_id', 'direction_id')
    raw_id_fields = ('author',)

@admin.register(ProgramUser)
class ProgramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'program_id', 'role_id')
    search_fields = ('user_id__email', 'program_id__profile')
    list_filter = ('role_id',)

@admin.register(NsiType)
class NsiTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'part', 'active', 'created_at', 'updated_at')
    search_fields = ('name', 'code')
    list_filter = ('active',)

@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'short_nominative', 'short_genitive', 'created_at', 'updated_at')
    search_fields = ('fullname', 'short_nominative', 'short_genitive')

@admin.register(Nsi)
class NsiAdmin(admin.ModelAdmin):
    list_display = ('id','nsiFullName', 'type', 'program', 'author', 'nsiCode', 'nsiYear', 'nsiCity', 'created_at', 'updated_at')
    search_fields = ('nsiName', 'nsiCode', 'nsiFullName')
    list_filter = ('type', 'nsiYear')
    raw_id_fields = ('author', 'program', 'nsiMinistry')


@admin.register(StageType)
class StageTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'stage_number', 'code')  # Поля, отображаемые в списке
    ordering = ('stage_number',)  # Сортировка в админке
    search_fields = ('name', 'code')  # Поля для поиска
    list_filter = ('code',)  # Боковые фильтры


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('program', 'stage_type', 'result')  # Поля, отображаемые в списке
    list_filter = ('program', 'stage_type')  # Боковые фильтры
    search_fields = ('program__profile', 'stage_type__name')  # Поля для поиска


@admin.register(WizardType)
class WizardTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')  # Поля, отображаемые в списке
    search_fields = ('name', 'code')  # Поля для поиска


@admin.register(StepType)
class StepTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'wizard_type', 'position')  # Поля, отображаемые в списке
    list_filter = ('wizard_type',)  # Боковые фильтры
    search_fields = ('name', 'code', 'wizard_type__name')  # Поля для поиска
    ordering = ('wizard_type', 'position')  # Сортировка по мастеру и позиции


@admin.register(Wizard)
class WizardAdmin(admin.ModelAdmin):
    list_display = ('program', 'wizard_type', 'created_at')  # Поля, отображаемые в списке
    list_filter = ('program', 'wizard_type')  # Боковые фильтры
    search_fields = ('program__profile', 'wizard_type__name')  # Поля для поиска
    date_hierarchy = 'created_at'  # Фильтр по дате создания


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ('wizard', 'step_type', 'created_at')  # Поля, отображаемые в списке
    list_filter = ('wizard', 'step_type')  # Боковые фильтры
    search_fields = ('wizard__program__profile', 'step_type__name', 'result')  # Поля для поиска
    date_hierarchy = 'created_at'  # Фильтр по дате создания


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'program', 'position', 'get_nsis')  # Поля, отображаемые в списке
    list_filter = ('program',)  # Боковой фильтр
    search_fields = ('name', 'description', 'program__profile')  # Поля для поиска
    ordering = ('program', 'position')  # Сортировка

    def get_nsis(self, obj):
        # Отображаем связанные NSIs в виде строки через запятую
        return ", ".join([nsi.nsiName for nsi in obj.nsis.all()])
    get_nsis.short_description = 'NSIs'  # Название колонки в админке